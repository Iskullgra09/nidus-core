from typing import Any, cast
from uuid import UUID

import jwt
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError, NidusException
from app.core.security import create_access_token, create_password_reset_token, hash_password, verify_password
from app.models import Member, User


class AuthService:
    @staticmethod
    async def authenticate(session: AsyncSession, email: str, password: str) -> str:
        """
        Validates credentials against active users and returns a JWT.
        Standardized with Dynamic Model Aliases for clean SQLAlchemy syntax.
        """
        await session.execute(text("SET LOCAL app.current_organization_id = ''"))
        await session.execute(text("SET LOCAL app.current_user_id = ''"))

        UserModel = cast(Any, User)
        MemberModel = cast(Any, Member)

        stmt = select(User).where(
            UserModel.email == email,
            UserModel.deleted_at.is_(None),
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError(message_key="auth.invalid_credentials")

        member_stmt = select(Member).where(
            MemberModel.user_id == user.id,
            MemberModel.deleted_at.is_(None),
        )
        member_result = await session.execute(member_stmt)
        membership = member_result.scalar_one_or_none()

        if not membership:
            raise NidusException(code="NO_ACTIVE_ORG", message_key="common.forbidden", status_code=403)

        token_data = {"sub": str(user.id), "org_id": str(membership.organization_id)}
        return create_access_token(token_data)

    @staticmethod
    async def forgot_password(session: AsyncSession, email: str) -> str | None:
        """
        Finds the user and generates a reset token.
        Security best practice: Returns None if user not found, avoiding email enumeration.
        """
        UserModel = cast(Any, User)
        stmt = select(User).where(UserModel.email == email, UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            return None

        return create_password_reset_token(str(user.id))

    @staticmethod
    async def reset_password(session: AsyncSession, token: str, new_password: str) -> None:
        """Validates token and updates password."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str = payload.get("sub")
            token_type = payload.get("type")

            if token_type != "reset_password" or not user_id_str:
                raise AuthenticationError(message_key="auth.invalid_token")

        except jwt.ExpiredSignatureError:
            raise AuthenticationError(message_key="auth.token_expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError(message_key="auth.invalid_token")

        UserModel = cast(Any, User)
        stmt = select(User).where(UserModel.id == UUID(user_id_str), UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            raise EntityNotFoundError(entity="user")

        user.hashed_password = hash_password(new_password)
        await session.commit()

    @staticmethod
    async def change_password(session: AsyncSession, user_id: UUID, current_password: str, new_password: str) -> None:
        """Allows an authenticated user to change their own password."""
        UserModel = cast(Any, User)
        stmt = select(User).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            raise EntityNotFoundError(entity="user")

        if not verify_password(current_password, user.hashed_password):
            raise ConflictError(message_key="auth.wrong_current_password")

        user.hashed_password = hash_password(new_password)
        await session.commit()
