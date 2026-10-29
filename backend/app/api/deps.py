from typing import Annotated, Any, cast
from uuid import UUID

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.db import get_session
from app.core.exceptions.base import AuthenticationError, NidusException
from app.core.i18n.request import get_request_language
from app.core.rls import set_rls_context
from app.models.identity.member import Member
from app.models.identity.scopes import NidusScope

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_jwt_payload(token: Annotated[str, Depends(oauth2_scheme)]) -> dict[str, Any]:
    """Extracts and validates the JWT payload with strict dictionary typing."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not payload.get("sub") or not payload.get("org_id"):
            raise AuthenticationError(message_key="auth.invalid_token")
        return payload
    except Exception:
        raise AuthenticationError(message_key="auth.token_expired")


async def get_current_tenant_session(
    payload: Annotated[dict[str, Any], Depends(get_jwt_payload)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncSession:
    """
    Injects the JWT context into PostgreSQL RLS.
    Returns the database session tightly scoped to the current tenant.
    """
    user_id = payload.get("sub")
    org_id = payload.get("org_id")

    await set_rls_context(session, org_id, user_id)
    return session


def get_language(request: Request) -> str:
    """Extracts preferred language from the request."""
    return get_request_language(request)


async def get_current_org_id(
    payload: Annotated[dict[str, Any], Depends(get_jwt_payload)],
) -> UUID:
    """Returns the active organization id from the JWT (tenant context)."""
    return UUID(str(payload["org_id"]))


class ScopeGuard:
    """
    Evaluates hierarchical JSONB scopes.
    Fast path: JWT embedded scopes (issued at login/switch-org).
    Fallback: DB role lookup for legacy tokens missing scopes.
    """

    def __init__(self, required_scope: str):
        self.required_scope = required_scope

    async def __call__(
        self,
        session: Annotated[AsyncSession, Depends(get_current_tenant_session)],
        payload: Annotated[dict[str, Any], Depends(get_jwt_payload)],
    ) -> bool:
        jwt_scopes = payload.get("scopes")
        if isinstance(jwt_scopes, list) and jwt_scopes:
            if NidusScope.grants_access(jwt_scopes, self.required_scope):
                return True

        user_id = payload.get("sub")
        MemberModel = cast(Any, Member)

        stmt = (
            select(Member)
            .where(
                MemberModel.user_id == user_id,
                MemberModel.deleted_at.is_(None),
            )
            .options(selectinload(MemberModel.role))
        )

        result = await session.execute(stmt)
        member = result.scalar_one_or_none()
        role = cast(Any, member).role if member else None

        if not member or not role or role.deleted_at is not None:
            raise NidusException(code="NO_ACTIVE_ROLE", message_key="common.forbidden", status_code=403)

        if not NidusScope.grants_access(role.scopes, self.required_scope):
            raise NidusException(
                code="MISSING_SCOPE",
                message_key="common.unauthorized",
                status_code=403,
                scope=self.required_scope,
            )

        return True
