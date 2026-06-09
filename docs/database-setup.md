# NIDUS Database Setup

## Dual database model

| Database | Used by |
|----------|---------|
| `nidus_core` | Local dev (`uv run fastapi dev`), manual UI testing, Mailtrap flows |
| `nidus_core_test` | `pytest` only — truncated before every test |

## Dual PostgreSQL role model (both databases)

| Role | Purpose |
|------|---------|
| `nidus_admin` | Alembic migrations, test truncate/seed — bypasses RLS |
| `nidus_app_user` | FastAPI runtime & pytest API calls — RLS enforced |

## First-time setup

```powershell
# 1. Start Postgres
docker compose up -d db

# 2. Migrate development database
cd backend
uv run alembic upgrade head

# 3. Migrate test database (required before pytest)
uv run python scripts/migrate_test_db.py

# 4. Run tests (never touches nidus_core)
uv run pytest -v
```

## After schema changes

Always run both migration commands:

```powershell
uv run alembic upgrade head
uv run python scripts/migrate_test_db.py
```

## Cleaning polluted dev data

If test users appeared in `nidus_core` before ADR 048, you can remove them manually:

```sql
-- Connect as nidus_admin to nidus_core
TRUNCATE invitation, member, role, "user", organization RESTART IDENTITY CASCADE;
```

Then re-onboard via the UI or Swagger.
