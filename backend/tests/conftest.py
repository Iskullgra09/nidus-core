# ruff: noqa: E402
import os
import uuid
from typing import Any, AsyncGenerator, Dict, List, Tuple, cast

import pytest
from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

ADMIN_DB_URL = settings.TEST_DATABASE_URL
APP_DB_URL = settings.DATABASE_URL
os.environ["DATABASE_URL"] = APP_DB_URL

from app.main import app
from app.models import Organization
from app.models.identity.role import Role

app_engine = create_async_engine(APP_DB_URL, poolclass=NullPool)
app_session_maker = async_sessionmaker(app_engine, class_=AsyncSession, expire_on_commit=False)

admin_engine = create_async_engine(ADMIN_DB_URL, poolclass=NullPool)
admin_session_maker = async_sessionmaker(admin_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
def override_db_setup(monkeypatch: MonkeyPatch) -> None:
    """
    Globally overrides the production database engine with the test engine.
    Ensures no accidental writes to production-like environments occur during testing.
    """
    import app.core.db

    monkeypatch.setattr(app.core.db, "engine", app_engine)
    monkeypatch.setattr(app.core.db, "async_session_maker", app_session_maker)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an AsyncSession with 'nidus_app_user' privileges.
    RLS policies are strictly enforced for this session.
    """
    async with app_session_maker() as session:
        yield session


@pytest.fixture
async def admin_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an AsyncSession with 'nidus_admin' privileges.
    Bypasses RLS policies. To be used exclusively for setup and verification.
    """
    async with admin_session_maker() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Initializes an asynchronous HTTP client for integration testing.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture(autouse=True)
async def cleanup_and_seed() -> None:
    """
    Synchronizes the database state before each test execution.
    Utilizes administrative privileges to bypass RLS for data seeding.
    """
    async with admin_session_maker() as session:
        async with session.begin():
            tables_to_truncate: List[str] = ["invitation", "member", "role", '"user"', "organization"]
            for table in tables_to_truncate:
                await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

            test_org = Organization(name="Global Test Corp", slug="test-corp", is_active=True)
            session.add(test_org)
            await session.flush()

            if not test_org.id:
                raise RuntimeError("Critical: Failed to generate Test Organization ID.")

            system_roles: List[Dict[str, Any]] = [
                {"name": "Admin", "desc": "Full administrative access", "scopes": ["*"]},
                {"name": "Member", "desc": "Standard read-only access", "scopes": ["identity:user:read"]},
            ]

            for r_data in system_roles:
                new_role = Role(
                    name=cast(str, r_data["name"]),
                    description=cast(str, r_data["desc"]),
                    organization_id=test_org.id,
                    scopes=cast(List[str], r_data["scopes"]),
                )
                session.add(new_role)


@pytest.fixture
async def auth_client(async_client: AsyncClient) -> AsyncGenerator[Tuple[AsyncClient, dict[str, Any]], None]:
    """
    Fixture that handles onboarding and login automatically.
    Returns the authenticated client and the generated organization data.
    """
    uid = str(uuid.uuid4())[:8]
    email = f"test-{uid}@nidus.com"
    password = "TestPassword123!"

    onboarding_payload = {
        "organization_name": f"Org {uid}",
        "organization_slug": f"slug-{uid}",
        "admin_email": email,
        "password": password,
    }
    res = await async_client.post("/api/v1/organizations/onboarding", json=onboarding_payload)
    org_data = res.json()["data"]

    login_res = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]

    async_client.headers.update({"Authorization": f"Bearer {token}"})

    yield async_client, {"org_id": org_data["organization_id"], "user_id": org_data["user_id"]}

    async_client.headers.pop("Authorization", None)
