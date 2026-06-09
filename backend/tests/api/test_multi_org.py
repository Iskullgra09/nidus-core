import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_multi_org_login_requires_selection(async_client: AsyncClient) -> None:
    uid = str(uuid.uuid4())[:8]
    email = f"multi-{uid}@nidus.com"
    password = "TestPassword123!"

    for slug_suffix, org_name in [("a", "Org Alpha"), ("b", "Org Beta")]:
        res = await async_client.post(
            "/api/v1/organizations/onboarding",
            json={
                "organization_name": org_name,
                "organization_slug": f"slug-{slug_suffix}-{uid}",
                "admin_email": email,
                "password": password,
            },
        )
        assert res.status_code == 201

    login_res = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_res.status_code == 200
    payload = login_res.json()["data"]

    assert payload["org_selection_required"] is True
    assert len(payload["organizations"]) == 2
    assert "pre_auth_token" in payload
    assert "access_token" not in payload


@pytest.mark.asyncio
async def test_select_org_and_switch_org(async_client: AsyncClient) -> None:
    uid = str(uuid.uuid4())[:8]
    email = f"switch-{uid}@nidus.com"
    password = "TestPassword123!"

    org_ids = []
    for slug_suffix, org_name in [("a", "Org Alpha"), ("b", "Org Beta")]:
        res = await async_client.post(
            "/api/v1/organizations/onboarding",
            json={
                "organization_name": org_name,
                "organization_slug": f"slug-{slug_suffix}-{uid}",
                "admin_email": email,
                "password": password,
            },
        )
        org_ids.append(res.json()["data"]["organization_id"])

    login_res = await async_client.post("/api/v1/auth/login", data={"username": email, "password": password})
    login_payload = login_res.json()["data"]

    select_res = await async_client.post(
        "/api/v1/auth/select-org",
        json={"pre_auth_token": login_payload["pre_auth_token"], "organization_id": org_ids[1]},
    )
    assert select_res.status_code == 200
    token = select_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_res = await async_client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["data"]["organization"]["id"] == org_ids[1]

    orgs_res = await async_client.get("/api/v1/users/me/organizations", headers=headers)
    assert orgs_res.status_code == 200
    assert len(orgs_res.json()["data"]) == 2

    switch_res = await async_client.post(
        "/api/v1/auth/switch-org",
        json={"organization_id": org_ids[0]},
        headers=headers,
    )
    assert switch_res.status_code == 200
    new_token = switch_res.json()["data"]["access_token"]

    me_after_switch = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert me_after_switch.status_code == 200
    assert me_after_switch.json()["data"]["organization"]["id"] == org_ids[0]
