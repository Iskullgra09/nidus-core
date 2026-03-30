from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_organization_id

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=(settings.ENVIRONMENT == "development"),
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Base session generator.
    In the future, we will wrap this to inject the organization_id.
    """
    async with async_session_maker() as session:
        yield session


async def set_session_tenant(session: AsyncSession, org_id: UUID) -> None:
    """
    Injects the organization_id into the PostgreSQL session.
    """
    await session.execute(
        text("SELECT set_config('app.current_organization_id', :org_id, false)"),
        {"org_id": str(org_id)},
    )


async def get_tenant_session(
    org_id: UUID = Depends(get_organization_id),
) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        await set_session_tenant(session, org_id)
        yield session
