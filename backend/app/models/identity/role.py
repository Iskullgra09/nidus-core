from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.member import Member
    from app.models.organization.organization import Organization


class Role(UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin, table=True):
    name: str = Field()
    description: Optional[str] = Field(default=None)
    scopes: List[str] = Field(default=[], sa_column=sa.Column(postgresql.JSONB, server_default="[]", nullable=False))

    organization: Optional["Organization"] = Relationship(back_populates="roles")
    members: List["Member"] = Relationship(back_populates="role")

    __table_args__ = (
        sa.Index("ix_role_scopes_gin", "scopes", postgresql_using="gin", postgresql_ops={"scopes": "jsonb_path_ops"}),
        sa.Index("ix_role_name_org_active", "name", "organization_id", unique=True, postgresql_where=sa.text("deleted_at IS NULL")),
    )
