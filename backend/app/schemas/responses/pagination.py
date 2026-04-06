from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")


class PageInfo(BaseModel):
    """Metadata for the frontend to know how to load the next page."""

    has_next_page: bool
    end_cursor: Optional[UUID] = None


class CursorPage(BaseModel, Generic[T]):
    """Standardized wrapper for paginated lists."""

    items: List[T]
    page_info: PageInfo
