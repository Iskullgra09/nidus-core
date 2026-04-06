import httpx
import pytest


@pytest.mark.asyncio
async def test_health_check(async_client: httpx.AsyncClient):
    response = await async_client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert data["message"] == "NIDUS Core is running"
    assert data["version"] == "v1"
