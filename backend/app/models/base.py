import uuid
from datetime import datetime, timezone
from typing import Any, Optional, cast

import sqlalchemy as sa
from sqlalchemy import func, text
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
        sa_type=cast(Any, sa.DateTime(timezone=True)),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=cast(Any, sa.DateTime(timezone=True)),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


class TenantMixin(SQLModel):
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True, nullable=False)


class SoftDeleteMixin(SQLModel):
    """
    Mixin for logical deletion.
    Using sa_type=cast(Any, ...) ensures Pylance stays green while
    SQLModel clones the column correctly across all tables.
    """

    deleted_at: Optional[datetime] = Field(
        default=None,
        index=True,
        nullable=True,
        sa_type=cast(Any, sa.DateTime(timezone=True)),
        description="Timestamp for soft delete auditing",
    )

    def trigger_soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
