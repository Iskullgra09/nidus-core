from typing import TYPE_CHECKING, Any, Dict, List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.member import Member


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    email: str = Field()
    hashed_password: str = Field()
    full_name: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    preferences: Dict[str, Any] = Field(
        default_factory=dict, sa_column=sa.Column(JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False)
    )
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    memberships: List["Member"] = Relationship(back_populates="user")

    __table_args__ = (sa.Index("ix_user_email_active", "email", unique=True, postgresql_where=sa.text("deleted_at IS NULL")),)
