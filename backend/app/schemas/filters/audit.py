from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogFilter(BaseModel):
    action: Optional[str] = Field(default=None, description="Exact audit action code, e.g. auth.login")
    actor_user_id: Optional[UUID] = None
    resource_type: Optional[str] = None
