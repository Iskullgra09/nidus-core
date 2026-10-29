from typing import Any, cast
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.base import EntityNotFoundError
from app.core.media import delete_avatar_file, save_avatar
from app.models import Member, User
from app.schemas.requests.user import UpdateProfileRequest
from app.schemas.responses.user import UserProfileResponse


class UserService:
    @staticmethod
    async def get_my_profile(session: AsyncSession, user_id: UUID) -> UserProfileResponse:
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
            avatar_url=m.user.avatar_url,
            preferences=m.user.preferences,
            is_superuser=m.user.is_superuser,
            role_name=m.role.name,
            scopes=m.role.scopes,
            organization=m.organization,
        )

    @staticmethod
    async def set_avatar(session: AsyncSession, user_id: UUID, file: UploadFile) -> str:
        UserModel = cast(Any, User)
        stmt = select(User).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            raise EntityNotFoundError(entity="user")

        delete_avatar_file(user.avatar_url)
        url = await save_avatar(file, kind="users", entity_id=user_id)
        user.avatar_url = url
        await session.commit()
        return url

    @staticmethod
    async def clear_avatar(session: AsyncSession, user_id: UUID) -> None:
        UserModel = cast(Any, User)
        stmt = select(User).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            raise EntityNotFoundError(entity="user")

        delete_avatar_file(user.avatar_url)
        user.avatar_url = None
        await session.commit()

    @staticmethod
    async def update_profile(session: AsyncSession, user_id: UUID, data: UpdateProfileRequest) -> None:
        """Updates the user's personal details and preferences."""
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return

        UserModel = cast(Any, User)

        if "preferences" in update_data and update_data["preferences"] is not None:
            stmt = select(User).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
            user = (await session.execute(stmt)).scalar_one_or_none()
            if not user:
                raise EntityNotFoundError(entity="user")

            merged_preferences = {**(user.preferences or {}), **update_data["preferences"]}
            update_data["preferences"] = merged_preferences

        stmt = update(User).where(UserModel.id == user_id).values(**update_data)
        await session.execute(stmt)
        await session.commit()
