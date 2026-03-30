import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_organization_me_endpoint(async_client: AsyncClient):
    """
    Final Integration Test:
    1. Onboarding (Create Org/User)
    2. Login (Get JWT Token)
    3. GET /me (Verify RLS & Identity)
    """
    uid = str(uuid.uuid4())[:8]
    email = f"owner-{uid}@nidus.com"
    slug = f"corp-{uid}"
    password = "secure_password123"

    onboarding_payload = {
        "organization_name": "Test Corp",
        "organization_slug": slug,
        "admin_email": email,
        "password": password,
    }

    onboarding_res = await async_client.post("/api/v1/organizations/onboarding", json=onboarding_payload)
    assert onboarding_res.status_code == 201
    org_id = onboarding_res.json()["data"]["organization_id"]

    login_data = {"username": email, "password": password}
    login_res = await async_client.post("/api/v1/auth/login", data=login_data)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/v1/organizations/me", headers=headers)

    assert response.status_code == 200
    res_json = response.json()

    assert res_json["status"] == "success"
    assert "data" in res_json

    org_data = res_json["data"]
    assert org_data["id"] == org_id
    assert org_data["slug"] == slug
    assert org_data["name"] == "Test Corp"
