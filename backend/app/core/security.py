from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from uuid import UUID

import bcrypt
import jwt
from fastapi import Header
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_organization_id(
    x_organization_id: Annotated[
        UUID, Header(description="The unique ID of the organization")
    ],
) -> UUID:
    """
    Dependency that extracts the organization_id from the 'X-Organization-ID' header.
    If the header is missing or is not a valid UUID, FastAPI will return a 422 error.
    """

    return x_organization_id


def hash_password(password: str) -> str:
    """Returns a secure bcrypt hash using the direct bcrypt library."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict[str, Any]) -> str:
    """Creates a signed JWT token with organization context."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
