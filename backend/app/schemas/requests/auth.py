from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    """Payload to request a password reset email."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Payload to set a new password using a token."""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Payload for authenticated users to change their password."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
