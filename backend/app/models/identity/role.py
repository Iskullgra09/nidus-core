from sqlmodel import Field

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Role(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    name: str = Field(unique=True, index=True, nullable=False)
    description: str | None = Field(default=None)
