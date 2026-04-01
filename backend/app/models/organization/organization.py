from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.invitation import Invitation
    from app.models.identity.member import Member
    from app.models.identity.role import Role


class Organization(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    name: str = Field(index=True)
    slug: str = Field()
    is_active: bool = Field(default=True)

    members: List["Member"] = Relationship(back_populates="organization")
    roles: List["Role"] = Relationship(back_populates="organization")
    invitations: List["Invitation"] = Relationship(back_populates="organization")

    __table_args__ = (sa.Index("ix_organization_slug_active", "slug", unique=True, postgresql_where=sa.text("deleted_at IS NULL")),)
