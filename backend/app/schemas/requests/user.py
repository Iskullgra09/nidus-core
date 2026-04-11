from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.responses.user import UserPreferencesSchema


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    preferences: Optional[UserPreferencesSchema] = None
