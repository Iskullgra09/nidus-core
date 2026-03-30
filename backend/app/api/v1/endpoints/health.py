from datetime import datetime, timezone

from app.core.db import get_session
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.health import HealthResponse
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", response_model=GenericResponse[HealthResponse])
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Sanity check for the API and Database connection.
    """
    db_status = "unreachable"
    try:
        await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    health_data = HealthResponse(
        status="ok",
        version="1.0.0",
        environment="development",
        timestamp=datetime.now(timezone.utc),
        database_status=db_status,
    )

    return GenericResponse(data=health_data, message="System is operational")
