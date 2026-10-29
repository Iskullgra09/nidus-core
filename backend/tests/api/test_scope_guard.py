import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthenticated_cannot_update_organization(async_client: AsyncClient) -> None:
    response = await async_client.patch("/api/v1/organizations/me", json={"name": "Hacked Name"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_cannot_list_roles(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/identity/roles")
    assert response.status_code == 401
