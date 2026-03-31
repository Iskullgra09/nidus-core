from typing import Any, cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import Member, Organization, User
from app.models.identity.role import Role
from app.schemas.requests.tenant import TenantCreate


class OrganizationService:
    @staticmethod
    async def create_onboarding(session: AsyncSession, data: TenantCreate) -> tuple[UUID, UUID]:
        """
        Orchestrates the Atomic Onboarding process with Soft Delete awareness.
        """
        existing_org_stmt = select(Organization).where(
            cast(ColumnElement[bool], Organization.slug == data.organization_slug),
            cast(ColumnElement[bool], cast(Any, Organization.deleted_at).is_(None)),
        )
        existing_org_result = await session.execute(existing_org_stmt)

        if existing_org_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization slug already registered and active.",
            )

        try:
            user_stmt = select(User).where(
                cast(ColumnElement[bool], User.email == data.admin_email), cast(ColumnElement[bool], cast(Any, User.deleted_at).is_(None))
            )
            user_result = await session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if not user:
                user = User(
                    email=data.admin_email,
                    hashed_password=hash_password(data.password),
                    is_active=True,
                )
                session.add(user)
                await session.flush()

            new_org = Organization(name=data.organization_name, slug=data.organization_slug, is_active=True)
            session.add(new_org)
            await session.flush()

            role_stmt = select(Role).where(
                cast(ColumnElement[bool], Role.name == "Admin"), cast(ColumnElement[bool], cast(Any, Role.deleted_at).is_(None))
            )
            role_result = await session.execute(role_stmt)
            admin_role = role_result.scalar_one_or_none()

            if not admin_role:
                admin_role = Role(name="Admin", description="Full access to the organization")
                session.add(admin_role)
                await session.flush()

            new_member = Member(
                user_id=user.id,
                organization_id=new_org.id,
                role_id=admin_role.id,
            )
            session.add(new_member)

            await session.commit()
            return new_org.id, user.id

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Onboarding failed: {str(e)}",
            )
