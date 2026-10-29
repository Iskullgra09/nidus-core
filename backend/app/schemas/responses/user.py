from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.responses.organization import OrganizationResponse


class UserPreferencesSchema(BaseModel):
    language: str = "en"
    theme: str = "system"


class UserProfileResponse(BaseModel):
    """Complete profile of the authenticated user within the current tenant context."""

    id: UUID
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: UserPreferencesSchema = UserPreferencesSchema()
    is_superuser: bool
    role_name: str
    scopes: List[str]
    organization: OrganizationResponse

    model_config = ConfigDict(from_attributes=True)
