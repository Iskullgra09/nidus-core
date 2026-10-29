from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MemberFilter(BaseModel):
    """
    Defines allowed filterable fields for Organization Members.
    Naming convention: field__operator (standard in 2026).
    """

    role_name: Optional[str] = Field(None, alias="role")

    email__contains: Optional[str] = None

    is_active: Optional[bool] = None

    model_config = ConfigDict(populate_by_name=True)


class InvitationFilter(BaseModel):
    """Filter for listing organization invitations."""

    is_accepted: Optional[bool] = Field(False, alias="accepted")
    email__contains: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)
