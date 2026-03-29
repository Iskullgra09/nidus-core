from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session


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
