from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Role(UUIDMixin, TimestampMixin, SoftDeleteMixin, table=True):
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)

    scopes: List[str] = Field(default=[], sa_column=Column(JSONB, server_default="[]", nullable=False))
