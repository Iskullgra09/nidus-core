from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationResponse(BaseModel):
    """How an organization looks when returned to the client."""

    id: UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OnBoardingResponse(BaseModel):
    """Schema for the successful onboarding response."""

    organization_id: UUID
    user_id: UUID
