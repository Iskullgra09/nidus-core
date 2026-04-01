from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, identity, organization

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(organization.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(identity.router, prefix="/identity", tags=["identity"])
