from uuid import UUID

from pydantic import BaseModel


class UserOrganizationSummary(BaseModel):
    """Organization membership visible to the authenticated user."""

    organization_id: UUID
    name: str
    slug: str
    role_name: str
