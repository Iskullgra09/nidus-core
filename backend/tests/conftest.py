# ruff: noqa: E402
import os
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import col, select

ADMIN_DB_URL = "postgresql+asyncpg://nidus_admin:nidus_local_secret@localhost:5444/nidus_test"
APP_DB_URL = "postgresql+asyncpg://nidus_app_user:nidus_app_secret@localhost:5444/nidus_test"
os.environ["DATABASE_URL"] = APP_DB_URL

from app.main import app
from app.models.identity.role import Role

app_engine = create_async_engine(APP_DB_URL, poolclass=NullPool)
app_session_maker = async_sessionmaker(app_engine, class_=AsyncSession, expire_on_commit=False)

admin_engine = create_async_engine(ADMIN_DB_URL, poolclass=NullPool)
admin_session_maker = async_sessionmaker(admin_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
def override_db_setup(monkeypatch: MonkeyPatch):
    import app.core.db

    monkeypatch.setattr(app.core.db, "engine", app_engine)
    monkeypatch.setattr(app.core.db, "async_session_maker", app_session_maker)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    THIS IS THE KEY: Use this fixture in your tests instead of
    importing async_session_maker directly.
    """
    async with app_session_maker() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture(autouse=True)
async def cleanup_and_seed():
    """Cleanup before each test using Admin privileges."""

    async with admin_session_maker() as session:
        async with session.begin():
            tables = ["member", '"user"', "organization"]
            for table in tables:
                await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

            for r_name in ["Admin", "Member"]:
                stmt = select(Role).where(col(Role.name) == r_name)
                res = await session.execute(stmt)
                if not res.scalar_one_or_none():
                    session.add(Role(name=r_name, description=f"{r_name} role"))
