from typing import Any, cast
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.base import EntityNotFoundError
from app.models import Member, User
from app.schemas.requests.user import UpdateProfileRequest
from app.schemas.responses.user import UserProfileResponse


class UserService:
    @staticmethod
    async def get_my_profile(session: AsyncSession, user_id: UUID) -> UserProfileResponse:
        """
        Retrieves the complete profile for the authenticated user,
        including their current organization and role context.
        """
        MemberModel = cast(Any, Member)

        stmt = (
            select(Member)
            .where(MemberModel.user_id == user_id, MemberModel.deleted_at.is_(None))
            .options(selectinload(MemberModel.user), selectinload(MemberModel.role), selectinload(MemberModel.organization))
        )
        result = await session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise EntityNotFoundError(entity="user_profile")

        m = cast(Any, member)

        return UserProfileResponse(
            id=m.user.id,
            email=m.user.email,
            full_name=m.user.full_name,
            preferences=m.user.preferences,
            is_superuser=m.user.is_superuser,
            role_name=m.role.name,
            scopes=m.role.scopes,
            organization=m.organization,
        )

    @staticmethod
    async def update_profile(session: AsyncSession, user_id: UUID, data: UpdateProfileRequest) -> None:
        """Updates the user's personal details and preferences."""
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return

        UserModel = cast(Any, User)

        stmt = update(User).where(UserModel.id == user_id).values(**update_data)
        await session.execute(stmt)
        await session.commit()
