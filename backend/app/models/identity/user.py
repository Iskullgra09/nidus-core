from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.member import Member


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    email: str = Field(index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)

    memberships: List["Member"] = Relationship(back_populates="user")
