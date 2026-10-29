import uuid
from typing import Any, Dict, Tuple

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlmodel import col

from app.models.identity.role import Role
from app.models.identity.scopes import DefaultRole, NidusScope


@pytest.mark.asyncio
async def test_list_roles(auth_client: Tuple[AsyncClient, Dict[str, Any]]) -> None:
    client, _ = auth_client
    response = await client.get("/api/v1/identity/roles")
    assert response.status_code == 200
    roles = response.json()["data"]
    assert len(roles) == 4
    assert all("is_system" in role for role in roles)


@pytest.mark.asyncio
async def test_custom_role_crud(auth_client: Tuple[AsyncClient, Dict[str, Any]]) -> None:
    client, _ = auth_client

    create_payload = {
        "name": "Billing Manager",
        "description": "Can read org and members",
        "scopes": [NidusScope.ORG_READ.value, NidusScope.MEMBER_READ.value],
    }
    create_res = await client.post("/api/v1/identity/roles", json=create_payload)
    assert create_res.status_code == 201
    role_id = create_res.json()["data"]["id"]
    assert create_res.json()["data"]["is_system"] is False

    update_res = await client.patch(
        f"/api/v1/identity/roles/{role_id}",
        json={"description": "Updated description"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["description"] == "Updated description"

    delete_res = await client.delete(f"/api/v1/identity/roles/{role_id}")
    assert delete_res.status_code == 200


@pytest.mark.asyncio
async def test_cannot_modify_system_role(auth_client: Tuple[AsyncClient, Dict[str, Any]], db_session) -> None:
    client, context = auth_client
    org_id = context["org_id"]

    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{org_id}'"))
        owner_role = (
            await db_session.execute(
                select(Role).where(col(Role.name) == DefaultRole.OWNER.value, col(Role.organization_id) == uuid.UUID(org_id))
            )
        ).scalar_one()

    patch_res = await client.patch(
        f"/api/v1/identity/roles/{owner_role.id}",
        json={"description": "Hacked"},
    )
    assert patch_res.status_code == 409


@pytest.mark.asyncio
async def test_list_and_revoke_invitations(auth_client: Tuple[AsyncClient, Dict[str, Any]], db_session) -> None:
    client, context = auth_client
    org_id = context["org_id"]

    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{org_id}'"))
        member_role = (
            await db_session.execute(
                select(Role).where(col(Role.name) == DefaultRole.MEMBER.value, col(Role.organization_id) == uuid.UUID(org_id))
            )
        ).scalar_one()

    invite_res = await client.post(
        "/api/v1/identity/invitations",
        json={"email": "pending@nidus.com", "role_id": str(member_role.id)},
    )
    assert invite_res.status_code == 201
    invitation_id = invite_res.json()["data"]["id"]

    list_res = await client.get("/api/v1/identity/invitations")
    assert list_res.status_code == 200
    pending = list_res.json()["data"]
    assert len(pending) == 1
    assert pending[0]["email"] == "pending@nidus.com"
    assert pending[0]["role_name"] == DefaultRole.MEMBER.value

    revoke_res = await client.delete(f"/api/v1/identity/invitations/{invitation_id}")
    assert revoke_res.status_code == 200

    empty_res = await client.get("/api/v1/identity/invitations")
    assert empty_res.status_code == 200
    assert len(empty_res.json()["data"]) == 0


@pytest.mark.asyncio
async def test_list_scopes(auth_client: Tuple[AsyncClient, Dict[str, Any]]) -> None:
    client, _ = auth_client
    response = await client.get("/api/v1/identity/scopes")
    assert response.status_code == 200
    values = {item["value"] for item in response.json()["data"]}
    assert NidusScope.SUPERADMIN.value not in values
    assert NidusScope.ORG_READ.value in values
