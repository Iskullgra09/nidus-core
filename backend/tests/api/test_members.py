import uuid
from typing import Any, Dict, Tuple

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models.identity.role import Role
from app.models.identity.scopes import DefaultRole


@pytest.mark.asyncio
async def test_list_members_with_filters_and_pagination(auth_client: Tuple[AsyncClient, Dict[str, Any]]) -> None:
    """Tests the cursor pagination and dynamic filtering engine for members."""
    client, _ = auth_client

    response = await client.get("/api/v1/identity/members")
    assert response.status_code == 200
    data = response.json()["data"]

    assert len(data["items"]) == 1
    assert data["items"][0]["role_name"] == "Owner"

    filter_res = await client.get("/api/v1/identity/members?role=Admin")
    assert filter_res.status_code == 200
    assert len(filter_res.json()["data"]["items"]) == 0

    page_res = await client.get("/api/v1/identity/members?limit=1")
    page_data = page_res.json()["data"]

    assert len(page_data["items"]) == 1
    assert page_data["page_info"]["has_next_page"] is False


@pytest.mark.asyncio
async def test_invite_member_happy_path(auth_client: Tuple[AsyncClient, Dict[str, Any]], db_session: AsyncSession) -> None:
    """
    Happy Path: Owner can invite a new member.
    Uses db_session and .value to query the Role Enum safely.
    """
    client, context = auth_client
    org_id = context["org_id"]

    role_id_str = ""
    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{org_id}'"))

        stmt = select(Role).where(col(Role.name) == DefaultRole.MEMBER.value, col(Role.organization_id) == uuid.UUID(org_id))
        role_db = (await db_session.execute(stmt)).scalar_one_or_none()

        assert role_db is not None, "Member role was not bootstrapped properly!"
        role_id_str = str(role_db.id)

    payload = {"email": "new_coworker@nidus.com", "role_id": role_id_str}

    response = await client.post("/api/v1/identity/invitations", json=payload)

    assert response.status_code == 201
    res_json = response.json()
    assert res_json["status"] == "success"
    assert res_json["data"]["email"] == "new_coworker@nidus.com"


@pytest.mark.asyncio
async def test_unauthorized_member_access(async_client: AsyncClient) -> None:
    """Sad Path: Accessing members endpoint without a valid JWT token."""
    response = await async_client.get("/api/v1/identity/members")
    assert response.status_code == 401
