from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NIDUS Core Multitenant API",
)

_media_root = Path(settings.MEDIA_ROOT)
_media_root.mkdir(parents=True, exist_ok=True)
app.mount(settings.MEDIA_URL_PATH, StaticFiles(directory=str(_media_root)), name="media")

# RequestContextMiddleware outermost so it wraps CORS + all handlers.
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.FRONTEND_URL), "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
