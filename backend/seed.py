import asyncio
from typing import Any, cast

from sqlalchemy import select, text

from app.core.db import async_session_maker
from app.core.security import hash_password
from app.models import Member, Organization, User
from app.models.identity.role import Role
from app.models.identity.scopes import DefaultRole


async def seed_data() -> None:
    """
    Seeds the database with 5 dummy members for testing purposes.
    Specifically assigns the 'Member' role to ensure data variety.
    """
    async with async_session_maker() as session:
        # 1. Bypass RLS for global seeding
        await session.execute(text("SET LOCAL app.current_organization_id = ''"))
        await session.execute(text("SET LOCAL app.current_user_id = ''"))

        RoleModel = cast(Any, Role)

        # 2. Fetch the first available Organization
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalars().first()

        if not org:
            print("❌ Error: No Organization found. Run POST /onboarding in Swagger first.")
            return

        # 3. Fetch the 'Member' role for this specific organization
        role_stmt = select(Role).where(RoleModel.organization_id == org.id, RoleModel.name == DefaultRole.MEMBER)
        role_result = await session.execute(role_stmt)
        member_role = role_result.scalars().first()

        if not member_role:
            print(f"❌ Error: '{DefaultRole.MEMBER}' role not found for org: {org.name}")
            return

        print(f"🏗️  Seeding 5 members into organization: {org.name}...")

        # 4. Generate 5 Dummy Users
        for i in range(1, 6):
            email = f"test_user_{i}@niduslabs.com"

            # Check if user already exists to avoid unique constraint errors
            user = User(email=email, hashed_password=hash_password("Nidus2026!"), is_active=True)
            session.add(user)
            await session.flush()  # Obtain user.id

            # 5. Create Membership with the 'Member' role
            member = Member(user_id=user.id, organization_id=org.id, role_id=member_role.id)
            session.add(member)

        await session.commit()
        print(f"✅ Success! 5 members with role '{DefaultRole.MEMBER}' inserted.")


if __name__ == "__main__":
    asyncio.run(seed_data())
