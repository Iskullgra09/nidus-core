import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class TenantCreate(BaseModel):
    """Schema for creating a new Organization and its Admin User."""

    organization_name: str = Field(..., min_length=3, max_length=100)
    organization_slug: str = Field(..., min_length=3, max_length=50)

    admin_email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("organization_slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        return v
