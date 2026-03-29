from app.core.config import settings
from app.core.db import get_session
from app.schemas.health import HealthResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    """Check system and database connectivity."""
    try:
        result = await session.execute(text("SELECT 1"))
        is_db_up = result.scalar() == 1
        return HealthResponse(
            status="healthy",
            environment=settings.ENVIRONMENT,
            database_connected=is_db_up,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database down: {str(e)}")
