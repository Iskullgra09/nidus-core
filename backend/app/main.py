from app.core.config import settings
from app.shared.database import get_db_session
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NIDUS Core Multitenant API",
)


# 1. Define the strict response schema
class HealthResponse(BaseModel):
    status: str
    environment: str
    database_connected: bool


# 2. Add the return type hint and the FastAPI response_model
@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db_session)) -> HealthResponse:
    """
    Validates API routing and Database connectivity.
    """
    try:
        result = await db.execute(text("SELECT 1"))
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
