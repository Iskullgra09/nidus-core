import uuid

import pytest
from app.models.organization.infrastructure.models import Organization
from app.shared.database import async_session_maker
from sqlalchemy import select, text


@pytest.mark.asyncio
async def test_row_level_security_isolation():
    target_id = uuid.uuid4()
    hacker_id = uuid.uuid4()
    unique_name = f"Organization-{target_id}"

    # --- TEST 1: El camino feliz (Contexto Correcto) ---
    async with async_session_maker() as session:
        # Usamos SET LOCAL dentro de una transacción
        async with session.begin():
            await session.execute(
                text(f"SET LOCAL nidus.current_organization_id = '{target_id}'")
            )

            new_organization = Organization(id=target_id, name=unique_name)
            session.add(new_organization)
            await session.flush()

            # Debería ver exactamente 1 (el suyo)
            result = await session.execute(select(Organization))
            rows = result.scalars().all()
            assert len(rows) == 1
            assert rows[0].id == target_id

    # --- TEST 2: Intento de lectura sin contexto ---
    async with async_session_maker() as session:
        async with session.begin():
            # Limpiamos explícitamente el setting para esta conexión por si acaso
            await session.execute(text("SET LOCAL nidus.current_organization_id = ''"))

            result = await session.execute(select(Organization))
            rows = result.scalars().all()
            # Si RLS funciona, len(rows) DEBE ser 0, incluso si hay datos en la tabla
            assert len(rows) == 0

    # --- TEST 3: Intento de lectura con ID de otro inquilino ---
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(
                text(f"SET LOCAL nidus.current_organization_id = '{hacker_id}'")
            )

            result = await session.execute(select(Organization))
            rows = result.scalars().all()
            assert len(rows) == 0
