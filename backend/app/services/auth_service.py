from typing import Any, Dict, List, Union, cast
from uuid import UUID

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions.base import AuthenticationError, ConflictError, EntityNotFoundError, NidusException
from app.core.rls import clear_rls_context
from app.core.security import (
    create_access_token,
    create_org_selection_token,
    create_password_reset_token,
    hash_password,
    verify_password,
)
from app.models import Member, User
from app.schemas.responses.auth import UserOrganizationSummary


class AuthService:
    @staticmethod
    async def _reset_rls_context(session: AsyncSession) -> None:
        await clear_rls_context(session)

    @staticmethod
    async def validate_credentials(session: AsyncSession, email: str, password: str) -> User:
        await AuthService._reset_rls_context(session)

        UserModel = cast(Any, User)
        stmt = select(User).where(UserModel.email == email, UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError(message_key="auth.invalid_credentials")

        return user

    @staticmethod
    async def get_active_memberships(session: AsyncSession, user_id: UUID) -> List[Member]:
        await AuthService._reset_rls_context(session)

        MemberModel = cast(Any, Member)
        stmt = (
            select(Member)
            .where(MemberModel.user_id == user_id, MemberModel.deleted_at.is_(None))
            .options(selectinload(MemberModel.role), selectinload(MemberModel.organization))
            .order_by(MemberModel.created_at.asc())
        )
        result = await session.execute(stmt)
        memberships = [m for m in result.scalars().all() if m.role and m.organization and m.role.deleted_at is None]

        return memberships

    @staticmethod
    def _build_token_for_membership(user: User, membership: Member) -> str:
        user_scopes: List[str] = ["*"] if user.is_superuser else list(membership.role.scopes)
        token_data: Dict[str, Any] = {
            "sub": str(user.id),
            "org_id": str(membership.organization_id),
            "scopes": user_scopes,
        }
        return create_access_token(token_data)

    @staticmethod
    def _membership_to_summary(membership: Member) -> UserOrganizationSummary:
        org = cast(Any, membership).organization
        role = cast(Any, membership).role
        return UserOrganizationSummary(
            organization_id=membership.organization_id,
            name=org.name,
            slug=org.slug,
            role_name=role.name,
        )

    @staticmethod
    async def list_user_organizations(session: AsyncSession, user_id: UUID) -> List[UserOrganizationSummary]:
        memberships = await AuthService.get_active_memberships(session, user_id)
        return [AuthService._membership_to_summary(m) for m in memberships]

    @staticmethod
    async def login(
        session: AsyncSession,
        email: str,
        password: str,
    ) -> Union[Dict[str, str], Dict[str, Any]]:
        user = await AuthService.validate_credentials(session, email, password)
        memberships = await AuthService.get_active_memberships(session, user.id)

        if not memberships:
            raise NidusException(code="NO_ACTIVE_ORG", message_key="common.forbidden", status_code=403)

        if len(memberships) == 1:
            token = AuthService._build_token_for_membership(user, memberships[0])
            return {"access_token": token, "token_type": "bearer"}

        return {
            "org_selection_required": True,
            "pre_auth_token": create_org_selection_token(str(user.id)),
            "organizations": [AuthService._membership_to_summary(m).model_dump(mode="json") for m in memberships],
        }

    @staticmethod
    async def select_organization(session: AsyncSession, pre_auth_token: str, organization_id: UUID) -> str:
        try:
            payload = jwt.decode(pre_auth_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str = payload.get("sub")
            token_type = payload.get("type")
            if token_type != "org_selection" or not user_id_str:
                raise AuthenticationError(message_key="auth.invalid_token")
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(message_key="auth.token_expired")
        except (jwt.InvalidTokenError, Exception):
            raise AuthenticationError(message_key="auth.invalid_token")

        user_id = UUID(str(user_id_str))
        memberships = await AuthService.get_active_memberships(session, user_id)
        membership = next((m for m in memberships if m.organization_id == organization_id), None)

        if not membership:
            raise EntityNotFoundError(entity="organization")

        UserModel = cast(Any, User)
        user = (await session.execute(select(User).where(UserModel.id == user_id, UserModel.deleted_at.is_(None)))).scalar_one_or_none()
        if not user:
            raise EntityNotFoundError(entity="user")

        return AuthService._build_token_for_membership(user, membership)

    @staticmethod
    async def switch_organization(session: AsyncSession, user_id: UUID, organization_id: UUID) -> str:
        memberships = await AuthService.get_active_memberships(session, user_id)
        membership = next((m for m in memberships if m.organization_id == organization_id), None)

        if not membership:
            raise EntityNotFoundError(entity="organization")

        UserModel = cast(Any, User)
        user = (await session.execute(select(User).where(UserModel.id == user_id, UserModel.deleted_at.is_(None)))).scalar_one_or_none()
        if not user:
            raise EntityNotFoundError(entity="user")

        return AuthService._build_token_for_membership(user, membership)

    @staticmethod
    async def forgot_password(session: AsyncSession, email: str) -> str | None:
        UserModel = cast(Any, User)
        await AuthService._reset_rls_context(session)
        stmt = select(User).where(UserModel.email == email, UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            return None

        return create_password_reset_token(str(user.id))

    @staticmethod
    async def reset_password(session: AsyncSession, token: str, new_password: str) -> None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str = payload.get("sub")
            token_type = payload.get("type")

            if token_type != "reset_password" or not user_id_str:
                raise AuthenticationError(message_key="auth.invalid_token")

        except jwt.ExpiredSignatureError:
            raise AuthenticationError(message_key="auth.token_expired")
        except (jwt.InvalidTokenError, Exception):
            raise AuthenticationError(message_key="auth.invalid_token")

        UserModel = cast(Any, User)
        await AuthService._reset_rls_context(session)
        stmt = select(User).where(UserModel.id == UUID(user_id_str), UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            raise EntityNotFoundError(entity="user")

        user.hashed_password = hash_password(new_password)
        await session.commit()

    @staticmethod
    async def change_password(session: AsyncSession, user_id: UUID, current_password: str, new_password: str) -> None:
        UserModel = cast(Any, User)
        await AuthService._reset_rls_context(session)
        stmt = select(User).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            raise EntityNotFoundError(entity="user")

        if not verify_password(current_password, user.hashed_password):
            raise ConflictError(message_key="auth.wrong_current_password")

        user.hashed_password = hash_password(new_password)
        await session.commit()
