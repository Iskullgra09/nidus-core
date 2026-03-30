import uuid

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization.organization import Organization


@pytest.mark.asyncio
async def test_row_level_security_isolation(db_session: AsyncSession):
    """
    RLS Isolation Test:
    1. Create an organization as a 'Target' using the empty string bypass.
    2. Verify the Target can see its own data.
    3. Verify a 'Hacker' (different ID) cannot see the data.
    """
    target_id = uuid.uuid4()
    hacker_id = uuid.uuid4()
    unique_name = f"Organization-{target_id}"
    unique_slug = f"slug-{target_id}"

    async with db_session.begin():
        await db_session.execute(text("SET LOCAL app.current_organization_id = ''"))

        new_organization = Organization(id=target_id, name=unique_name, slug=unique_slug, is_active=True)
        db_session.add(new_organization)

    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{target_id}'"))

        result = await db_session.execute(select(Organization))
        rows = result.scalars().all()

        assert len(rows) == 1
        assert rows[0].id == target_id
    async with db_session.begin():
        await db_session.execute(text(f"SET LOCAL app.current_organization_id = '{hacker_id}'"))

        result = await db_session.execute(select(Organization))
        rows = result.scalars().all()

        assert len(rows) == 0, "SECURITY BREACH: Hacker accessed Target's data!"
