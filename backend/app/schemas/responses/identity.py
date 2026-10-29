from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InvitationResponse(BaseModel):
    id: UUID
    email: str
    role_id: UUID
    role_name: str | None = None
    expires_at: datetime
    is_accepted: bool


class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: Optional[str] = None
    email: str
    avatar_url: Optional[str] = None
    role_name: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvitationAcceptedResponse(BaseModel):
    user_id: UUID
    organization_id: UUID
    role_id: UUID


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    scopes: list[str]
    is_system: bool = False

    model_config = ConfigDict(from_attributes=True)


class ScopeResponse(BaseModel):
    value: str
    group: str
