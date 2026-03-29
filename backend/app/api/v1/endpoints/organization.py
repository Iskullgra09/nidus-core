from app.core.db import get_session, get_tenant_session
from app.models import Organization
from app.schemas.tenant import TenantCreate, TenantResponse
from app.services.tenant_service import TenantService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/my-organization")
async def get_current_organization(session: AsyncSession = Depends(get_tenant_session)):
    """Returns the organization matching the X-Organization-ID header."""
    result = await session.execute(select(Organization))
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    return organization


@router.post(
    "/onboarding", response_model=TenantResponse, status_code=status.HTTP_201_CREATED
)
async def onboard_tenant(
    data: TenantCreate,
    session: AsyncSession = Depends(get_session),
):

    return await TenantService.create_onboarding(session, data)
