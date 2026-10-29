from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class InvitationCreate(BaseModel):
    email: EmailStr
    role_id: UUID


class MemberUpdateRole(BaseModel):
    role_id: UUID


class InvitationAccept(BaseModel):
    token: str = Field(..., min_length=10)
    password: str = Field(..., min_length=8)


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    scopes: list[str] = Field(..., min_length=1)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    scopes: Optional[list[str]] = Field(None, min_length=1)
