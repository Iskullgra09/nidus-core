from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, identity, organization, users

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System"])
api_router.include_router(organization.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(identity.router, prefix="/identity", tags=["Identity & Invitations"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
