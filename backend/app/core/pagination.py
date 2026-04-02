from typing import Any, Optional, Sequence, Tuple, TypeVar
from uuid import UUID

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Any)


async def paginate_with_cursor(
    session: AsyncSession, stmt: Select[Tuple[ModelType]], model_class: Any, limit: int, cursor: Optional[UUID] = None
) -> Tuple[Sequence[ModelType], Optional[UUID], bool]:
    """
    Executes a highly optimized Keyset (Cursor) Pagination query leveraging UUIDv7.
    Assumes descending order (newest first).
    """
    query = stmt

    if cursor:
        query = query.where(model_class.id < cursor)

    query = query.order_by(model_class.id.desc()).limit(limit + 1)

    result = await session.execute(query)
    items: Sequence[ModelType] = result.scalars().all()

    has_next_page = len(items) > limit

    items_to_return = items[:limit]

    end_cursor = items_to_return[-1].id if has_next_page and items_to_return else None
    return items_to_return, end_cursor, has_next_page
