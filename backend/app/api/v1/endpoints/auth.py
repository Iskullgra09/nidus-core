# app/api/v1/endpoints/auth.py
from app.core.db import get_session
from app.services.auth_service import AuthService
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """
    Standard OAuth2 compatible token login.
    Returns the access token with organization context.
    """
    token = await AuthService.authenticate(
        session, email=form_data.username, password=form_data.password
    )
    return {"access_token": token, "token_type": "bearer"}
