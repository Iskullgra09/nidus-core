from uuid import UUID

from pydantic import BaseModel


class TenantResponse(BaseModel):
    """Schema for the successful onboarding response."""

    organization_id: UUID
    user_id: UUID
