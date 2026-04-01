import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Optional, cast

import sqlalchemy as sa
from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization.organization import Organization


class Invitation(UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin, table=True):
    email: str = Field(index=True)
    role_id: uuid.UUID = Field(foreign_key="role.id")
    token: str = Field(default_factory=lambda: uuid.uuid4().hex, index=True)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7), sa_type=cast(Any, sa.DateTime(timezone=True))
    )
    is_accepted: bool = Field(default=False)
    accepted_at: Optional[datetime] = Field(default=None, sa_type=cast(Any, sa.DateTime(timezone=True)))

    organization: Optional["Organization"] = Relationship(back_populates="invitations")

    __table_args__ = (sa.Index("ix_invitation_token_unique", "token", unique=True),)
