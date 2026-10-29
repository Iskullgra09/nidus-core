from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base import TenantMixin, UUIDMixin


class AuditLog(UUIDMixin, TenantMixin, table=True):
    """
    Append-only tenant audit trail.
    No SoftDeleteMixin / no updated_at — rows are immutable after insert.
    """

    __tablename__ = "audit_log"

    actor_user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", index=True)
    action: str = Field(index=True, max_length=64)
    resource_type: Optional[str] = Field(default=None, max_length=64)
    resource_id: Optional[UUID] = Field(default=None, index=True)
    # `metadata` is reserved by SQLAlchemy; map Python attr → column name.
    details: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=sa.Column(
            "metadata",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    ip_address: Optional[str] = Field(default=None, max_length=45)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=cast(Any, sa.DateTime(timezone=True)),
        sa_column_kwargs={"server_default": sa.func.now()},
        index=True,
    )

    __table_args__ = (sa.Index("ix_audit_log_org_created", "organization_id", "id"),)
