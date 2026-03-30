from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class GenericResponse(BaseModel, Generic[T]):
    """Standardized response wrapper for the entire API."""

    status: str = "success"
    message: str | None = None
    data: T | None = None
