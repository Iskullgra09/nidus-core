from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.member import Member
    from app.models.identity.role import Role


class Organization(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    name: str = Field(index=True, nullable=False)
    slug: str = Field(index=True, nullable=False)
    is_active: bool = Field(default=True)

    members: List["Member"] = Relationship(back_populates="organization")
    roles: List["Role"] = Relationship(back_populates="organization")
