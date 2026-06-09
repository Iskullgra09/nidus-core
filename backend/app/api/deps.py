from typing import Annotated, Any, Set, cast

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.db import get_session
from app.core.exceptions.base import AuthenticationError, NidusException
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

    await session.execute(text(f"SET LOCAL app.current_organization_id = '{org_id}'"))
    await session.execute(text(f"SET LOCAL app.current_user_id = '{user_id}'"))
    return session


def get_language(request: Request) -> str:
    """Extracts preferred language from the request."""
    accept_lang = request.headers.get("accept-language", "en")
    return accept_lang.split(",")[0].split("-")[0].lower()


class ScopeGuard:
    """
    Dependency for evaluating Hierarchical JSONB Scopes.
    Uses the Dynamic Model Alias pattern to ensure Pylance strict compatibility.
    """

    def __init__(self, required_scope: str):
        self.required_scope = required_scope

    async def __call__(
        self,
        session: Annotated[AsyncSession, Depends(get_current_tenant_session)],
        payload: Annotated[dict[str, Any], Depends(get_jwt_payload)],
    ) -> bool:
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

        user_scopes: Set[str] = set(role.scopes)

        if NidusScope.SUPERADMIN in user_scopes:
            return True

        if self.required_scope in user_scopes:
            return True

        allowed_scopes = self._get_implied_scopes(self.required_scope)
        if user_scopes.intersection(allowed_scopes):
            return True

        raise NidusException(code="MISSING_SCOPE", message_key="common.unauthorized", status_code=403, scope=self.required_scope)

    def _get_implied_scopes(self, required_scope: str) -> Set[str]:
        """Calculates superset scopes."""
        allowed = {required_scope}
        if required_scope.endswith(":read"):
            allowed.add(required_scope.replace(":read", ":write"))
            allowed.add(required_scope.replace(":read", ":manage"))
        return allowed
