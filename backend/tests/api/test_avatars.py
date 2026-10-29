import io
from pathlib import Path

import pytest
from httpx import AsyncClient
from pytest import MonkeyPatch

from app.core.config import settings

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)


@pytest.fixture
def avatar_media_root(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_path))
    monkeypatch.setattr(settings, "PUBLIC_API_URL", "http://testserver")
    return tmp_path


@pytest.mark.asyncio
async def test_user_avatar_upload_and_delete(
    auth_client: tuple[AsyncClient, dict],
    avatar_media_root: Path,
) -> None:
    client, _ = auth_client

    upload = await client.post(
        "/api/v1/users/me/avatar",
        files={"file": ("avatar.png", io.BytesIO(PNG_1X1), "image/png")},
    )
    assert upload.status_code == 200
    body = upload.json()
    assert body["status"] == "success"
    url = body["data"]["avatar_url"]
    assert url.startswith("http://testserver/media/avatars/users/")

    profile = await client.get("/api/v1/users/me")
    assert profile.json()["data"]["avatar_url"] == url

    media_path = avatar_media_root / "avatars" / "users"
    assert any(media_path.glob("*.png"))

    delete = await client.delete("/api/v1/users/me/avatar")
    assert delete.status_code == 200
    profile_after = await client.get("/api/v1/users/me")
    assert profile_after.json()["data"]["avatar_url"] is None


@pytest.mark.asyncio
async def test_org_avatar_upload(
    auth_client: tuple[AsyncClient, dict],
    avatar_media_root: Path,
) -> None:
    client, _ = auth_client

    upload = await client.post(
        "/api/v1/organizations/me/avatar",
        files={"file": ("logo.png", io.BytesIO(PNG_1X1), "image/png")},
    )
    assert upload.status_code == 200
    url = upload.json()["data"]["avatar_url"]
    assert "/media/avatars/orgs/" in url

    profile = await client.get("/api/v1/users/me")
    assert profile.json()["data"]["organization"]["avatar_url"] == url


@pytest.mark.asyncio
async def test_avatar_rejects_invalid_type(
    auth_client: tuple[AsyncClient, dict],
    avatar_media_root: Path,
) -> None:
    client, _ = auth_client

    res = await client.post(
        "/api/v1/users/me/avatar",
        files={"file": ("note.txt", io.BytesIO(b"not-an-image"), "text/plain")},
    )
    assert res.status_code == 400
    assert res.json()["code"] == "INVALID_AVATAR_TYPE"
