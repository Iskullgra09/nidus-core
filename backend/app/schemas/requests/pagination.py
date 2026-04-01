from typing import Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel


class CursorParams(BaseModel):
    """
    Validates pagination query parameters.
    Protects the DB by enforcing a strict maximum limit.
    """

    limit: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)")
    cursor: Optional[UUID] = Query(default=None, description="UUIDv7 cursor for the next page")
