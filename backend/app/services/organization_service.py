from typing import Any, Dict, cast
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import ConflictError
from app.core.security import hash_password
from app.models import Member, Organization, User
from app.models.identity.role import Role
from app.models.identity.scopes import DEFAULT_ROLES_CONFIG, DefaultRole
from app.schemas.requests.tenant import TenantCreate


class OrganizationService:
    @staticmethod
    async def create_onboarding(session: AsyncSession, data: TenantCreate) -> tuple[UUID, UUID]:
        """
        Orchestrates the Atomic Onboarding process.
        Creates the organization and bootstraps the default role starter pack.
        Returns a tuple containing (organization_id, user_id).
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
                is_superuser=False,
            )
            session.add(user)
            await session.flush()

        new_org = Organization(name=data.organization_name, slug=data.organization_slug, is_active=True)
        session.add(new_org)
        await session.flush()

        created_roles: Dict[str, Role] = {}

        for role_name, config in DEFAULT_ROLES_CONFIG.items():
            new_role = Role(
                name=role_name,
                description=config["description"],
                organization_id=new_org.id,
                scopes=config["scopes"],
            )
            session.add(new_role)
            created_roles[role_name] = new_role

        await session.flush()

        new_member = Member(
            user_id=user.id,
            organization_id=new_org.id,
            role_id=created_roles[DefaultRole.OWNER].id,
        )
        session.add(new_member)

        await session.commit()

        return new_org.id, user.id
