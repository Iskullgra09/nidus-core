from sqlmodel import Field

from app.models.base import TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, table=True):
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
