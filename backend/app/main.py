from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions.base import NidusException
from app.core.exceptions.handlers import (
    global_500_exception_handler,
    nidus_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NIDUS Core Multitenant API",
)

app.add_exception_handler(NidusException, nidus_exception_handler)  # type: ignore
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(Exception, global_500_exception_handler)  # type: ignore

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "message": "NIDUS Core is running",
        "docs": "/docs",
        "version": "v1",
    }
