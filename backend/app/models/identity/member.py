import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.identity.role import Role
    from app.models.identity.user import User
    from app.models.organization.organization import Organization


class Member(UUIDMixin, TimestampMixin, SoftDeleteMixin, TenantMixin, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    role_id: uuid.UUID = Field(foreign_key="role.id", index=True)

    user: Optional["User"] = Relationship(back_populates="memberships")
    role: Optional["Role"] = Relationship(back_populates="members")
    organization: Optional["Organization"] = Relationship(back_populates="members")

    @property
    def email(self) -> str:
        return self.user.email if self.user else ""

    @property
    def role_name(self) -> str:
        return self.role.name if self.role else ""

    @property
    def joined_at(self) -> datetime:
        return self.created_at

    @property
    def full_name(self) -> Optional[str]:
        return self.user.full_name if self.user else None
