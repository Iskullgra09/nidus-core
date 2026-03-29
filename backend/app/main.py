from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session, get_tenant_session
from app.models import Organization


class HealthResponse(BaseModel):
    """Strict schema for system health monitoring."""

    status: str
    environment: str
    database_connected: bool
    version: str = "1.0.0"


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NIDUS Core Multitenant API",
)


@app.get("/health", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    """
    Validates system health and connectivity with PostgreSQL in Docker.
    """
    try:
        result = await session.execute(text("SELECT 1"))
        is_db_up = result.scalar() == 1

        return HealthResponse(
            status="healthy",
            environment=settings.ENVIRONMENT,
            database_connected=is_db_up,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Base entry point to verify the API Gateway is functional."""
    return {
        "project": settings.PROJECT_NAME,
        "message": "NIDUS Core is running",
        "docs": "/docs",
    }


@app.get("/my-organization")
async def get_current_organization(session: AsyncSession = Depends(get_tenant_session)):
    """
    This endpoint is PROTECTED by RLS.
    It only returns the organization that matches the X-Organization-ID header.
    """
    # Note: We don't use 'where(Organization.id == ...)'
    # The database will do it for us!
    result = await session.execute(select(Organization))
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found or you don't have access to it.",
        )

    return organization
