from sqlmodel import Field

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Organization(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    name: str = Field(index=True, nullable=False)
    slug: str = Field(index=True, nullable=False)
    is_active: bool = Field(default=True)
