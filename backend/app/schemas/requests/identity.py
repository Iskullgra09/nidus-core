from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: UUID


class MemberUpdateRole(BaseModel):
    """Payload for updating a member's role."""

    role_id: UUID


class InvitationAccept(BaseModel):
    """Payload for accepting an invitation and setting a password."""

    token: str = Field(..., min_length=10)
    password: str = Field(..., min_length=8)
