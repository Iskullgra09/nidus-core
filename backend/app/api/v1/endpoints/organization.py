from app.core.db import get_tenant_session
from app.models import Organization
from fastapi import APIRouter, Depends, HTTPException
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
