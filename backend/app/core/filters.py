from typing import Any, Generic, Tuple, Type, TypeVar, cast

from pydantic import BaseModel
from sqlalchemy import Select, String
from sqlalchemy import cast as sa_cast

T = TypeVar("T", bound=Any)


class FilterEngine(Generic[T]):
    """
    Advanced Filtering Engine for SQLAlchemy 2.0 & SQLModel.
    Type-safe implementation for 2026 standards.
    """

    def __init__(self, model: Type[T]):
        self.model = model

    def apply(self, query: Select[Tuple[T]], filters: BaseModel) -> Select[Tuple[T]]:
        """
        Applies dynamic filters to a Select statement.
        The query is typed as Select[Tuple[T]] to satisfy Pylance Strict.
        """
        filter_data = filters.model_dump(exclude_none=True)

        model_any = cast(Any, self.model)

        for field, value in filter_data.items():
            if "__" in field:
                attr_name, operator = field.split("__")
                if not hasattr(model_any, attr_name):
                    continue

                attr = getattr(model_any, attr_name)

                if operator == "contains":
                    query = query.where(sa_cast(attr, String).ilike(f"%{value}%"))
                elif operator == "gt":
                    query = query.where(attr > value)
                elif operator == "lt":
                    query = query.where(attr < value)
                elif operator == "in":
                    query = query.where(attr.in_(value))
            else:
                if hasattr(model_any, field):
                    attr = getattr(model_any, field)
                    query = query.where(attr == value)

        return query
