# Nidus Core

**The high-performance backbone for multitenant SaaS ecosystems.**

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)
![PostgreSQL 17/18](https://img.shields.io/badge/PostgreSQL-17/18-336791.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Nidus is an enterprise-grade monorepo designed for massive scale. It implements **Pragmatic Modular Monolith** patterns with hardware-level data isolation using **PostgreSQL Row-Level Security (RLS)** and **JSONB Granular Authorization**.

---

## Architectural Core

| Feature | Implementation |
| :--- | :--- |
| **Multitenancy** | Shared Schema + PostgreSQL RLS (Row-Level Security) |
| **Identity & IAM** | Hierarchical Scopes + GIN Indexed JSONB Authorization |
| **Persistence** | Async SQLModel + UUIDv7 Sequential Indexing |
| **Security** | Dual-Role Database Strategy (Migration Admin vs. App User) |
| **Reliability** | Global Soft-Delete & Timezone-Aware Temporal Mixins |
| **Observability** | Structured JSON request logs + append-only `audit_log` (RLS) |

### What belongs in Nidus Core (vs product forks)

Nidus Core is the **clone-ready platform**. Product domains (inventory, transactions, office/ops) live in **downstream repos**, not here.

| Layer (frontend) | Responsibility |
| :--- | :--- |
| `core/` | API client, i18n routing, theme â€” no feature imports |
| `shared/access` | `NidusScope`, `grantsAccess` / `hasScope` (mirrors backend) |
| `modules/identity` | Auth session, login/org switch, profile, password |
| `modules/access` | Roles, invitations, `CanAccess` |
| `modules/organization` | Tenant settings, members, org switcher, danger zone |
| `modules/shell` | Authenticated chrome (`TopBar`, Command Palette) |

Architecture decisions: `docs/architecture.md` (ADRs 049â€“055 for recent Core completion).

---

## Roadmap Status

| Phase | Focus | Status |
| :---: | :--- | :--- |
| 1 | Data Engine (RLS, baseline migration, security setup) | Done |
| 2 | Identity Base (JWT, BCrypt, atomic onboarding) | Done |
| 3 | RBAC & Governance (hierarchical scopes, GIN JSONB) | Done |
| 3.5 | Reliability (exception handlers, i18n, Pydantic 422) | Done |
| 3.6 | Lifecycle & Mail (async email, invitations, password recovery) | Done |
| 3.7 | Data Standard (UUIDv7 keyset pagination, soft-deletes) | Done |
| 4 | Frontend Foundation & Auth Pipeline (Next.js) | Done |
| 5 | Security & Access Loop (password reset, profile, preferences) | Done |
| 6 | Tenant Collaboration (org settings, invites, members UI) | Done |
| 7 | *(renumbered â€” see Phase 12)* | Moved |
| 8 | Infrastructure & DevOps (CORS, health, test DB isolation) | Done |
| 9 | Multi-Organization Sessions | Done |
| 10 | IAM Completion & Frontend Module Boundaries | Done |
| 11 | Observability & Audit | Done |
| 12 | Premium UX (Cmd+K, live dashboard, URL-driven members) | Done |
| 13 | DevEx & Containers (API image + compose) | Done |
| 14 | Security Hardening | Pending |
| 15 | Avatars & Media | Pending |
| 16 | CI Frontend & Quality Gates | Pending |

---

## Completed Phases (detail)

### Phases 1â€“3.7 â€” Backend foundation

- RLS policies, dual DB roles (`nidus_admin` / `nidus_app_user`), baseline Alembic migration.
- JWT auth, BCrypt, atomic tenant onboarding.
- Hierarchical `NidusScope`, role scopes in JSONB with GIN indexes, UUIDv7.
- Global exception handlers, EN/ES i18n, translated validation errors.
- Async email (`aiosmtplib`), invitation lifecycle, password recovery tokens.
- Cursor/keyset pagination, cascading soft-deletes.

### Phase 4 â€” Frontend foundation & auth

- Edge proxy JWT session validation (`src/proxy.ts`).
- Design system (Shadcn + Tailwind v4), Zod + React Hook Form.
- Login/logout Server Actions with HttpOnly cookies.
- `next-intl`, locale segments, tenant onboarding UI, Sonner toasts.

### Phase 5 â€” Security & access loop

- Forgot / reset password flows.
- Profile settings; theme and language preference persistence.

### Phase 6 â€” Tenant collaboration

- Organization settings (name/slug).
- Invitation dispatch, verify, and accept landing.
- Members data tables with RBAC-aware actions.

### Phase 8 â€” Infrastructure & DevOps

- [x] CORS for frontend origin + localhost.
- [x] Health check with DB connectivity probe.
- [x] pytest isolated on `nidus_core_test` (never `nidus_core`).
- [x] ADR 049: DB in Docker; primary DX keeps API/FE on host via `uv` / `pnpm`.

### Phase 9 â€” Multi-organization sessions

- [x] `GET /users/me/organizations`, `POST /auth/switch-org`, `POST /auth/select-org`.
- [x] Org picker on login; TopBar org switcher.
- [x] ADR 050.

### Phase 10 â€” IAM completion & module boundaries

- [x] Custom roles CRUD; invitations list/revoke; `NidusScope` FE/BE sync; roles UI.
- [x] Backend: IAM service split, `GenericResponse` everywhere, JWT scope fast path, org path guard (ADR 052).
- [x] Frontend: locale-safe routing, unified `grantsAccess`, `/organizations/me` + danger zone, modules `identity` / `access` / `organization` / `shell` (ADR 053).

### Phase 11 â€” Observability & audit

- [x] Structured JSON logging (`RequestContextMiddleware`, `X-Request-ID`).
- [x] Append-only `audit_log` + RLS; `AuditService`; event wiring for auth/IAM/org.
- [x] `GET /api/v1/audit-logs` gated by `audit:read` (ADR 054).

### Phase 12 â€” Premium UX

- [x] Command Palette (Cmd/Ctrl+K) in shell.
- [x] Dashboard with real Core data (members, orgs, health, recent audit when scoped).
- [x] Members URL tabs (`?tab=`) and cursor/search table (`?q=`, `?cursor=`).
- [x] ADR 055.

### Phase 13 â€” DevEx & containers

- [x] Root `Dockerfile` for FastAPI (uv multi-stage, non-root user).
- [x] `docker-compose.yml` API service fixed (build context, no broken bind mounts).
- [x] Entrypoint waits for Postgres, runs `alembic upgrade head`, then starts uvicorn.
- [x] Demo seed (`backend/seed.py`) â€” multi-org users/roles/invites; optional `SEED_DEMO=true`.
- [x] ADR 056 â€” API container delivered; FE stays on host.

---

## Upcoming Phases

### Phase 14 â€” Security hardening

- [ ] Rate limiting on auth and invitation endpoints.
- [ ] Session/cookie hardening review (SameSite, CSRF strategy as needed).
- [ ] Secrets and environment checklist for deployments.

### Phase 15 â€” Avatars & media

- [ ] User and organization avatar upload/storage.
- [ ] Safe content-type limits and URL serving strategy.

### Phase 16 â€” CI frontend & quality gates

- [ ] Frontend lint/typecheck (and tests when present) in GitHub Actions.
- [ ] Keep backend pytest on PR to `main`.
- [ ] Optional audit UI in settings (API already exists).

---

## Database Strategy (Dual DB + Dual Role)

| Database | Purpose | App user | Admin user |
| :--- | :--- | :--- | :--- |
| **`nidus_core`** | Development & manual usage (login, invites, Mailtrap) | `nidus_app_user` (RLS enforced) | `nidus_admin` (migrations only) |
| **`nidus_core_test`** | pytest & CI only â€” truncated before each test | `nidus_app_user` (RLS enforced) | `nidus_admin` (truncate/seed) |

**Never run pytest against `nidus_core`.** The test suite uses `TEST_APP_DATABASE_URL` and `TEST_DATABASE_URL` automatically.

---

## Operational Command Center

Use these commands from the project root. Ensure your `.env` is present at the root.

### Infrastructure (Docker)

Recommended clone flow: **DB + API in Docker**, frontend on the host with `pnpm`.

| Goal | Command |
| :--- | :--- |
| **Start DB + API** | `docker compose up -d --build` |
| **Start Only DB** (API via `uv` on host) | `docker compose up -d db` |
| **Stop Everything** | `docker compose stop` |
| **Full Wipe & Reset** | `docker compose down -v` |
| **View DB Logs** | `docker logs -f nidus-postgres` |
| **View API Logs** | `docker logs -f nidus-fastapi` |
| **Rebuild API image** | `docker compose build api --no-cache` |
| **Seed demo data** | `docker compose exec api python seed.py` |
| **Wipe DB volume** | `docker compose down -v` then `up -d --build` |

API listens on `http://localhost:8000` (docs at `/docs`). Compose overrides `POSTGRES_SERVER=db` inside the API container; host `uv` workflows keep `POSTGRES_SERVER=localhost` from `.env`.

#### Demo accounts (after seed)

Password for **all** demo users: `password123`

| Email | Access |
| :--- | :--- |
| `owner@acme.dev` | Owner â€” Acme Corp |
| `admin@acme.dev` | Admin (+ `audit:read`) â€” Acme |
| `member@acme.dev` | Member â€” Acme |
| `viewer@acme.dev` | Viewer â€” Acme |
| `multi@nidus.dev` | Acme Owner + Nidus Labs Member (org picker) |
| `owner@nidus.dev` | Owner â€” Nidus Labs |
| `admin@nidus.dev` | Admin â€” Nidus Labs |
| `member@nidus.dev` | Member â€” Nidus Labs |
| `owner@beta.dev` | Owner â€” Beta Partners |
| `viewer@beta.dev` | Viewer â€” Beta Partners |

Pending invites: `invitee@acme.dev`, `contractor@nidus.dev`, `partner@beta.dev`.

Or set `SEED_DEMO=true` in `.env` so the API container seeds automatically on start.

### Backend Development (Python / uv)

| Goal | Command |
| :--- | :--- |
| **Install Deps** | `uv sync` |
| **Run Migrations (dev DB)** | `uv run alembic upgrade head` |
| **Run Migrations (test DB)** | `uv run python scripts/migrate_test_db.py` |
| **Create Migration** | `uv run alembic revision --autogenerate -m "description"` |
| **Run Seed Script** | `uv run seed.py` |
| **Run Seed Script on Docker** | `docker exec -it nidus-fastapi python app/core/seed.py` |
| **Run API Locally** | `uv run fastapi dev app/main.py` |
| **Run Tests** | `uv run pytest` |

### Frontend Development (pnpm)

| Goal | Command |
| :--- | :--- |
| **Install Deps** | `pnpm install` |
| **Dev Mode** | `pnpm --filter nidus-frontend dev` |
| **Build Prod** | `pnpm --filter nidus-frontend build` |
| **Strict Typecheck** | `pnpm --filter nidus-frontend tsc --noEmit` |
| **Run Linter** | `pnpm --filter nidus-frontend lint` |
| **Add UI Component** | `pnpm --filter nidus-frontend dlx shadcn@latest add <component>` |
| **Clean cache** | `pnpm store prune` |

### Maintenance & Cleanup

| Goal | Command |
| :--- | :--- |
| **Fix Line Endings** | `dos2unix infrastructure/db-init/*.sh` (If utility is installed) |
| **Prune Volumes** | `docker volume prune -f` |

---

*Developed by Isaac Granados Quesada â€” Principal Engineer & Computer Architect.*
