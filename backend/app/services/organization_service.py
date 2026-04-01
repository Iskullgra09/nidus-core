from typing import Any, cast
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import ConflictError
from app.core.security import hash_password
from app.models import Member, Organization, User
from app.models.identity.role import Role
from app.schemas.requests.tenant import TenantCreate


class OrganizationService:
    @staticmethod
    async def create_onboarding(session: AsyncSession, data: TenantCreate) -> tuple[UUID, UUID]:
        """
        Orchestrates the Atomic Onboarding process with Soft Delete awareness.
        Uses Dynamic Model Aliases for clean Pylance-strict SQLAlchemy queries.
        """

        await session.execute(text("SET LOCAL app.current_organization_id = ''"))
        await session.execute(text("SET LOCAL app.current_user_id = ''"))

        OrgModel = cast(Any, Organization)
        UserModel = cast(Any, User)

        existing_org_stmt = select(Organization).where(
            OrgModel.slug == data.organization_slug,
            OrgModel.deleted_at.is_(None),
        )
        existing_org_result = await session.execute(existing_org_stmt)

        if existing_org_result.scalar_one_or_none():
            raise ConflictError(message_key="onboarding.org_already_exists", slug=data.organization_slug)

        user_stmt = select(User).where(UserModel.email == data.admin_email, UserModel.deleted_at.is_(None))
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

        admin_role = Role(
            name="Admin",
            description="Full access to the organization",
            organization_id=new_org.id,
            scopes=["*"],
        )
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
