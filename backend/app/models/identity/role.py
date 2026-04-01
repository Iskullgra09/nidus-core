from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.member import Member
    from app.models.organization.organization import Organization


class Role(UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin, table=True):
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)

    scopes: List[str] = Field(default=[], sa_column=Column(JSONB, server_default="[]", nullable=False))

    organization: Optional["Organization"] = Relationship(back_populates="roles")
    members: List["Member"] = Relationship(back_populates="role")
