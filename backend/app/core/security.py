from typing import Annotated
from uuid import UUID

from fastapi import Header


async def get_organization_id(
    x_organization_id: Annotated[
        UUID, Header(description="The unique ID of the organization")
    ],
) -> UUID:
    """
    Dependency that extracts the organization_id from the 'X-Organization-ID' header.
    If the header is missing or is not a valid UUID, FastAPI will return a 422 error.
    """

    return x_organization_id
