import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlmodel import col

from app.core.security import create_password_reset_token
from app.models.identity.user import User


@pytest.mark.asyncio
async def test_reset_password_flow(async_client: AsyncClient, db_session) -> None:
    uid = str(uuid.uuid4())[:8]
    email = f"reset-{uid}@nidus.com"
    password = "OldPassword123!"
    new_password = "NewPassword456!"

    onboarding = await async_client.post(
        "/api/v1/organizations/onboarding",
        json={
            "organization_name": f"Reset Org {uid}",
            "organization_slug": f"reset-{uid}",
            "admin_email": email,
            "password": password,
        },
    )
    assert onboarding.status_code == 201
    user_id = onboarding.json()["data"]["user_id"]

    async with db_session.begin():
        await db_session.execute(text("SET LOCAL app.current_organization_id = ''"))
        user = (await db_session.execute(select(User).where(col(User.id) == uuid.UUID(user_id)))).scalar_one()
        token = create_password_reset_token(str(user.id))

    reset_res = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": new_password},
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "success"

    login_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": new_password},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()["data"]


@pytest.mark.asyncio
async def test_change_password_flow(auth_client) -> None:
    client, _ = auth_client
    change_res = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "TestPassword123!", "new_password": "ChangedPass123!"},
    )
    assert change_res.status_code == 200
    assert change_res.json()["status"] == "success"
