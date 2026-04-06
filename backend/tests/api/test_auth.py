import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models.identity.member import Member
from app.models.identity.user import User
from app.models.organization.organization import Organization


@pytest.mark.asyncio
async def test_auth_and_onboarding_journey(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """
    Unified journey: Onboarding -> Login.
    Verifies API wrapper response and validates DB state using returned IDs.
    Uses db_session (same connection as the API) to avoid Split-Brain DB issues.
    """
    uid = str(uuid.uuid4())[:8]
    test_email = f"admin-{uid}@acme.com"
    test_slug = f"acme-{uid}"
    test_org_name = "Acme Corp"

    onboarding_payload = {
        "organization_name": test_org_name,
        "organization_slug": test_slug,
        "admin_email": test_email,
        "password": "secure_password123",
    }

    response = await async_client.post("/api/v1/organizations/onboarding", json=onboarding_payload)

    assert response.status_code == 201
    full_response = response.json()

    assert full_response["status"] == "success"
    assert "data" in full_response

    result_data = full_response["data"]
    org_id = result_data["organization_id"]
    user_id = result_data["user_id"]

    async with db_session.begin():
        await db_session.execute(text("SET LOCAL app.current_organization_id = ''"))

        org_stmt = select(Organization).where(col(Organization.id) == uuid.UUID(org_id))
        org_db = (await db_session.execute(org_stmt)).scalar_one_or_none()

        assert org_db is not None, "Organization not found! RLS bypass failed."
        assert org_db.slug == test_slug
        assert org_db.name == test_org_name

        user_stmt = select(User).where(col(User.id) == uuid.UUID(user_id))
        user_db = (await db_session.execute(user_stmt)).scalar_one_or_none()

        assert user_db is not None, "User not found!"
        assert user_db.email == test_email

        member_stmt = select(Member).where((col(Member.user_id) == uuid.UUID(user_id)) & (col(Member.organization_id) == uuid.UUID(org_id)))
        member_db = (await db_session.execute(member_stmt)).scalar_one_or_none()
        assert member_db is not None, "Member relation not found in DB"

    login_payload = {"username": test_email, "password": onboarding_payload["password"]}

    login_res = await async_client.post("/api/v1/auth/login", data=login_payload)

    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient) -> None:
    """Sad Path: Login with incorrect credentials."""
    login_payload = {"username": "nonexistent@acme.com", "password": "wrongpassword"}
    response = await async_client.post("/api/v1/auth/login", data=login_payload)

    assert response.status_code == 401
    assert response.json()["status"] == "error"


@pytest.mark.asyncio
async def test_forgot_password_enumeration_prevention(async_client: AsyncClient) -> None:
    """Security Test: Ensure forgot-password always returns 200 Success."""
    payload = {"email": "ghost_user@doesntexist.com"}
    response = await async_client.post("/api/v1/auth/forgot-password", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
