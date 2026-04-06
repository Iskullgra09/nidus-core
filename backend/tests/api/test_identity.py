from typing import Any, Dict, Tuple

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_me_endpoint_returns_full_profile(auth_client: Tuple[AsyncClient, Dict[str, Any]]) -> None:
    """
    Integration Test:
    GET /me (Verify Full Profile: User, Role, Organization)
    Utilizes the auth_client fixture to bypass repetitive manual login.
    """
    client, context = auth_client
    org_id = context["org_id"]
    user_id = context["user_id"]

    response = await client.get("/api/v1/organizations/me")

    assert response.status_code == 200
    res_json = response.json()

    assert res_json["status"] == "success"
    data = res_json["data"]

    assert data["id"] == str(user_id)
    assert data["role_name"] == "Owner"
    assert data["organization"]["id"] == str(org_id)


@pytest.mark.asyncio
async def test_update_organization_slug_conflict(auth_client: Tuple[AsyncClient, Dict[str, Any]], async_client: AsyncClient) -> None:
    """Sad Path: Attempting to update a slug to one that is already taken."""
    client, context = auth_client
    org_id = context["org_id"]

    await async_client.post(
        "/api/v1/organizations/onboarding",
        json={
            "organization_name": "Target Org",
            "organization_slug": "stolen-slug",
            "admin_email": "target@acme.com",
            "password": "password123",
        },
    )

    payload = {"slug": "stolen-slug"}
    response = await client.patch(f"/api/v1/organizations/{org_id}", json=payload)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_organization(auth_client: Tuple[AsyncClient, Dict[str, Any]]) -> None:
    """Happy Path: Soft delete the organization."""
    client, context = auth_client
    org_id = context["org_id"]

    response = await client.delete(f"/api/v1/organizations/{org_id}")
    assert response.status_code == 200

    me_response = await client.get("/api/v1/organizations/me")
    assert me_response.status_code in [401, 403, 404]
