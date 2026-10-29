from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions.base import NidusException

ALLOWED_AVATAR_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

_MAGIC: tuple[tuple[bytes, str], ...] = (
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
)


def _detect_content_type(header: bytes) -> str | None:
    for magic, content_type in _MAGIC:
        if header.startswith(magic):
            return content_type
    if len(header) >= 12 and header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image/webp"
    return None


def media_root() -> Path:
    root = Path(settings.MEDIA_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root


def public_media_url(relative_path: str) -> str:
    base = str(settings.PUBLIC_API_URL).rstrip("/")
    return f"{base}/{relative_path.lstrip('/')}"


def relative_path_from_public_url(url: str | None) -> str | None:
    if not url:
        return None
    base = str(settings.PUBLIC_API_URL).rstrip("/") + "/"
    if url.startswith(base):
        return url[len(base) :]
    prefix = settings.MEDIA_URL_PATH.strip("/") + "/"
    if f"/{prefix}" in url:
        idx = url.find(f"/{prefix}")
        return url[idx + 1 :]
    return None


async def save_avatar(file: UploadFile, *, kind: str, entity_id: UUID) -> str:
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_AVATAR_TYPES:
        raise NidusException(code="INVALID_AVATAR_TYPE", message_key="media.invalid_type", status_code=400)

    data = await file.read()
    if not data:
        raise NidusException(code="EMPTY_AVATAR", message_key="media.empty_file", status_code=400)
    if len(data) > settings.AVATAR_MAX_BYTES:
        raise NidusException(code="AVATAR_TOO_LARGE", message_key="media.too_large", status_code=400)

    detected = _detect_content_type(data[:16])
    if detected != content_type:
        raise NidusException(code="INVALID_AVATAR_TYPE", message_key="media.invalid_type", status_code=400)

    ext = ALLOWED_AVATAR_TYPES[content_type]
    relative_dir = f"{settings.MEDIA_URL_PATH.strip('/')}/avatars/{kind}"
    dest_dir = media_root() / "avatars" / kind
    dest_dir.mkdir(parents=True, exist_ok=True)

    for old in dest_dir.glob(f"{entity_id}.*"):
        old.unlink(missing_ok=True)

    dest = dest_dir / f"{entity_id}{ext}"
    dest.write_bytes(data)
    return public_media_url(f"{relative_dir}/{entity_id}{ext}")


def delete_avatar_file(avatar_url: str | None) -> None:
    relative = relative_path_from_public_url(avatar_url)
    if not relative:
        return
    path = media_root() / Path(relative).relative_to(settings.MEDIA_URL_PATH.strip("/"))
    if path.is_file():
        path.unlink(missing_ok=True)
