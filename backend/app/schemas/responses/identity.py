from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


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
