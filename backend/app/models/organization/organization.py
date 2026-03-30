from sqlmodel import Field

from app.models.base import TimestampMixin, UUIDMixin


class Organization(UUIDMixin, TimestampMixin, table=True):
    name: str = Field(index=True, nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)
    is_active: bool = Field(default=True)
