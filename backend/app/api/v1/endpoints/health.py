from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_language
from app.core.db import get_session
from app.core.i18n.service import i18n
from app.schemas.responses.base import GenericResponse
from app.schemas.responses.health import HealthResponse

router = APIRouter()


@router.get("/", response_model=GenericResponse[HealthResponse])
async def health_check(
    session: AsyncSession = Depends(get_session),
    lang: str = Depends(get_language),
):
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

    success_msg = i18n.t("success.system_operational", lang=lang)
    return GenericResponse(data=health_data, message=success_msg)
