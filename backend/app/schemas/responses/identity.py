from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


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
