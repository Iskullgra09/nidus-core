from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ScopeGuard, get_current_tenant_session
from app.core.db import get_session
from app.models.identity.scopes import NidusScope
from app.models.organization.organization import Organization
from app.schemas.requests.tenant import TenantCreate
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.organization import OrganizationResponse
from app.schemas.responses.tenant import TenantResponse
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.post(
    "/onboarding",
    response_model=GenericResponse[TenantResponse],
    status_code=status.HTTP_201_CREATED,
)
async def onboard_tenant(data: TenantCreate, session: AsyncSession = Depends(get_session)):
    """
    Creates a new organization, its first admin user, and assigns the correct roles.
    """
    org_id, user_id = await OrganizationService.create_onboarding(session, data)

    response_data = TenantResponse(
        organization_id=org_id,
        user_id=user_id,
        message="Onboarding completed successfully",
    )
    return GenericResponse(data=response_data, message="Welcome to NIDUS!")


@router.get("/me", response_model=GenericResponse[OrganizationResponse], dependencies=[Depends(ScopeGuard(NidusScope.ORG_READ))])
async def get_my_organization(
    session: AsyncSession = Depends(get_current_tenant_session),
):
    """
    Returns the organization details for the currently authenticated user.
    No need to pass IDs, the database RLS handles the isolation automatically.
    """
    stmt = select(Organization)
    result = await session.execute(stmt)

    org = result.scalar_one()

    return GenericResponse(data=org)
