from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.responses.organization import OrganizationResponse


class InvitationResponse(BaseModel):
    id: UUID
    email: EmailStr
    role_id: UUID
    token: str
    expires_at: datetime
    is_accepted: bool


class MemberResponse(BaseModel):
    id: UUID
    email: EmailStr
    role_name: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvitationAcceptedResponse(BaseModel):
    """Returned when a user successfully consumes an invitation token."""

    user_id: UUID
    organization_id: UUID
    role_id: UUID


class UserProfileResponse(BaseModel):
    """Complete profile of the authenticated user within the current tenant context."""

    id: UUID
    email: EmailStr
    is_superuser: bool
    role_name: str
    scopes: List[str]
    organization: OrganizationResponse

    model_config = ConfigDict(from_attributes=True)
