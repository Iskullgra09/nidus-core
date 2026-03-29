import uuid

from sqlmodel import Field

from app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class Member(UUIDMixin, TimestampMixin, TenantMixin, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="role.id")
