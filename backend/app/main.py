from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NIDUS Core Multitenant API",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "message": "NIDUS Core is running",
        "docs": "/docs",
        "version": "v1",
    }
