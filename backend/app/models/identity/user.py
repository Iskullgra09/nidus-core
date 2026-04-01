from typing import TYPE_CHECKING, List

import sqlalchemy as sa
from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.member import Member


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    email: str = Field()
    hashed_password: str = Field()
    is_active: bool = Field(default=True)

    memberships: List["Member"] = Relationship(back_populates="user")

    __table_args__ = (sa.Index("ix_user_email_active", "email", unique=True, postgresql_where=sa.text("deleted_at IS NULL")),)
