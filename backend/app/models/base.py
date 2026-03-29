import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class UUIDMixin(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "server_default": text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        },
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "server_default": text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            "onupdate": text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
        },
    )


class TenantMixin(SQLModel):
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", index=True, nullable=False
    )
