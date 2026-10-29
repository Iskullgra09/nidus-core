import pytest
from httpx import AsyncClient
from pytest import MonkeyPatch

from app.core.config import settings
from app.core.rate_limit import clear_rate_limit_store


@pytest.mark.asyncio
async def test_forgot_password_rate_limited(async_client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    clear_rate_limit_store()
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_STRICT_MAX", 3)
    monkeypatch.setattr(settings, "RATE_LIMIT_WINDOW_SECONDS", 60)

    payload = {"email": "rate-limit@example.com"}
    for _ in range(3):
        ok = await async_client.post("/api/v1/auth/forgot-password", json=payload)
        assert ok.status_code == 200

    blocked = await async_client.post("/api/v1/auth/forgot-password", json=payload)
    assert blocked.status_code == 429
    body = blocked.json()
    assert body["status"] == "error"
    assert body["code"] == "RATE_LIMIT_EXCEEDED"
    assert blocked.headers.get("retry-after") is not None
