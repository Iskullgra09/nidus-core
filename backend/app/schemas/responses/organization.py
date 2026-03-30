from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrganizationResponse(BaseModel):
    """How an organization looks when returned to the client."""

    id: UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
