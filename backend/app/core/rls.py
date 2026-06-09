from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _normalize_rls_value(value: str | UUID | None) -> str:
    if value is None:
        return ""
    return str(value)


async def set_rls_context(
    session: AsyncSession,
    organization_id: str | UUID | None,
    user_id: str | UUID | None,
) -> None:
    """Sets PostgreSQL RLS session variables using parameterized queries."""
    await session.execute(
        text("SELECT set_config('app.current_organization_id', :org_id, true)"),
        {"org_id": _normalize_rls_value(organization_id)},
    )
    await session.execute(
        text("SELECT set_config('app.current_user_id', :user_id, true)"),
        {"user_id": _normalize_rls_value(user_id)},
    )


async def clear_rls_context(session: AsyncSession) -> None:
    """Clears tenant RLS context for cross-tenant or public flows."""
    await set_rls_context(session, None, None)
