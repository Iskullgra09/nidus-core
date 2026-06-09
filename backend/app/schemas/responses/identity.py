from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class InvitationResponse(BaseModel):
    id: UUID
    email: EmailStr
    role_id: UUID
    expires_at: datetime
    is_accepted: bool


class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: Optional[str] = None
    email: EmailStr
    role_name: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvitationAcceptedResponse(BaseModel):
    """Returned when a user successfully consumes an invitation token."""

    user_id: UUID
    organization_id: UUID
    role_id: UUID


class RoleResponse(BaseModel):
    """Schema for returning role details to the frontend."""

    id: UUID
    name: str
    description: str | None = None
    scopes: list[str]

    model_config = ConfigDict(from_attributes=True)
