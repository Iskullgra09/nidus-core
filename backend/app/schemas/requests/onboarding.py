from pydantic import BaseModel, EmailStr


class OnboardingCreate(BaseModel):
    organization_name: str
    organization_slug: str
    admin_email: EmailStr
    password: str
