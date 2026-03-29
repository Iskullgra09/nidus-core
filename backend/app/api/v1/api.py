from app.api.v1.endpoints import health, organization
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(
    organization.router, prefix="/organizations", tags=["organizations"]
)
