import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class OrganizationUpdate(BaseModel):
    """Payload for updating organization details."""

    name: Optional[str] = Field(None, min_length=2, description="The new display name.")
    slug: Optional[str] = Field(None, min_length=2, pattern="^[a-z0-9-]+$", description="The new URL-friendly slug.")


class OnboardingCreate(BaseModel):
    """Schema for the initial signup process."""

    organization_name: str = Field(..., min_length=3, max_length=100)
    organization_slug: str = Field(..., min_length=3, max_length=50)
    admin_email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("organization_slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("validation.invalid_slug_format")
        return v
