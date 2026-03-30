from typing import cast

from app.core.security import create_access_token, verify_password
from app.models import Member, User
from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, select, text
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    @staticmethod
    async def authenticate(session: AsyncSession, email: str, password: str) -> str:
        """
        Validates credentials and returns a JWT with organization context.
        """

        await session.execute(text("SET LOCAL app.current_organization_id = ''"))
        await session.execute(text("SET LOCAL app.current_user_id = ''"))

        stmt = select(User).where(cast(ColumnElement[bool], User.email == email))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            print(f"DEBUG: Usuario con email {email} NO ENCONTRADO en la DB")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        print(f"DEBUG: Usuario encontrado: {user.email}. Hasheando para comparar...")

        if not verify_password(password, user.hashed_password):
            print("DEBUG: La contraseña NO coincide con el hash en la DB")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        member_stmt = select(Member).where(
            cast(ColumnElement[bool], Member.user_id == user.id)
        )
        member_result = await session.execute(member_stmt)
        membership = member_result.scalar_one_or_none()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned organization",
            )

        token_data = {"sub": str(user.id), "org_id": str(membership.organization_id)}

        return create_access_token(token_data)
