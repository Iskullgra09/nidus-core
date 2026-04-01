from uuid import UUID

from pydantic import BaseModel, EmailStr


class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: UUID


class MemberUpdateRole(BaseModel):
    role_id: UUID
