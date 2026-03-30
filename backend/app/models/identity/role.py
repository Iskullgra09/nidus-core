from sqlmodel import Field

from app.models.base import TimestampMixin, UUIDMixin


class Role(UUIDMixin, TimestampMixin, table=True):
    name: str = Field(unique=True, index=True, nullable=False)
    description: str | None = Field(default=None)
