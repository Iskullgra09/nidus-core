from typing import Any, cast

from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        member_stmt = select(Member).where(
            MemberModel.user_id == user.id,
            MemberModel.deleted_at.is_(None),
        )
        member_result = await session.execute(member_stmt)
        membership = member_result.scalar_one_or_none()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no active assigned organization",
            )

        token_data = {"sub": str(user.id), "org_id": str(membership.organization_id)}

        return create_access_token(token_data)
