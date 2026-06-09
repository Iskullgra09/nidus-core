# Nidus Core 
**The high-performance backbone for 2026+ Multitenant SaaS ecosystems.**

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

---

## Project Roadmap (Updated Q2 2026)

### Completed Milestones (Backend)
| Phase | Goal | Achievements |
| :--- | :--- | :--- |
| **1** | **Data Engine** | RLS Policies, Baseline Migration, Security Setup. |
| **2** | **Identity Base** | JWT stateless auth, BCrypt, Atomic Tenant Onboarding. |
| **3** | **RBAC & Governance** | Hierarchical Scopes, GIN-indexed Role Scopes, UUIDv7. |
| **3.5**| **Reliability Layer**| Global Exception Handlers, 100% i18n support, Pydantic 422 Translation. |
| **3.6**| **Lifecycle & Mail** | Asynchronous email dispatch (`aiosmtplib`), Secure Invitation Lifecycle, Password Recovery. |
| **3.7**| **The Data Standard**| O(1) Keyset Pagination via UUIDv7, Dynamic Pydantic-to-SQL Filtering Engine, Cascading Soft-Deletes. |

---

### In Progress / Upcoming (Frontend & Ecosystem)

#### **Phase 4: Frontend Foundation & Auth Pipeline** (Next.js 15)
- [x] **Gateway Proxy:** Edge routing and JWT session validation (`src/proxy.ts`).
- [x] **Design System:** Shadcn "Nova" + Tailwind v4 + OKLCH for predictable, high-density SaaS UI.
- [x] **Type-Safe Forms:** Zod (pinned to v3) + React Hook Form + Zero `any` policy.
- [x] **Authentication Flow:** Login Server Actions with HttpOnly cookie generation & Logout.
- [x] **Frontend i18n:** `next-intl` integration, Dynamic `[locale]` segments, and Zod Schema Factory.
- [x] **Tenant Onboarding:** Multilingual registration with automatic slugification.
- [x] **Unified Feedback:** Global Sonner Toaster with Server-Side translation bindings.

#### **Phase 5: The Security & Access Loop**
- [x] **Stateless Password Recovery:** Forgot Password (Email dispatch) and Reset Password (short-lived JWT) views.
- [x] **Profile Management:** User Settings view for name changes and avatar uploads.
- [x] **Preference Persistence:** Syncing UI Theme (Dark/Light) and Language (EN/ES) preferences to the DB.

#### **Phase 6: Tenant Collaboration (B2B Engine)**
- [x] **Organization Governance:** Org Settings view (Rename tenant, manage slug).
- [x] **Invitation Workflow:** Secure UI for dispatching invites, verifying tokens, and the "Accept Invitation" modular landing page.
- [x] **Member Management:** Dynamic Data Tables (Client/Server modes) with fixed-height UX, RBAC assignment, and conditional UI shielding.

#### **Phase 7: Premium UX & Developer-First Navigation** *(moved to Phase 12 below)*

---

### 🚧 In Progress — Core Platform Completion (`feat/core_completion`)

#### **Phase 8: Infrastructure & DevOps**
- [x] **CORS:** Explicit middleware for frontend origin + localhost.
- [x] **Health Check:** DB connectivity probe with environment-aware status.
- [x] **Test DB Isolation:** pytest uses `nidus_core_test` exclusively (never `nidus_core`).
- [ ] **Dockerfile** for FastAPI backend (optional while using `uv` locally).
- [ ] **Fix docker-compose.yml** API service volumes/context.
- [ ] ADR 049: Monorepo Container Strategy.

#### **Phase 9: Multi-Organization Sessions** *(critical)*
- [x] `GET /users/me/organizations` · `POST /auth/switch-org` · `POST /auth/select-org`.
- [x] Org picker on login (multi-membership users).
- [x] Org switcher in TopBar.
- [x] ADR 050: Multi-Organization Session Strategy.

#### **Phase 10: IAM Completion**
- [x] Custom roles CRUD · invitations list/revoke · sync `NidusScope` frontend ↔ backend · roles UI.

#### **Phase 11: Observability & Audit**
- [ ] Structured logging · `audit_log` table.

#### **Phase 12: Premium UX** *(original Phase 7)*
- [ ] Command Palette (Cmd+K) · modular sub-tabs · dashboard with real data · URL-driven server tables.

#### **Phase 13–16:** DevEx · Security hardening · Avatars · CI frontend/tests *(last)*.

---

## Database Strategy (Dual DB + Dual Role)

| Database | Purpose | App user | Admin user |
| :--- | :--- | :--- | :--- |
| **`nidus_core`** | Development & manual usage (login, invites, Mailtrap) | `nidus_app_user` (RLS enforced) | `nidus_admin` (migrations only) |
| **`nidus_core_test`** | pytest & CI only — truncated before each test | `nidus_app_user` (RLS enforced) | `nidus_admin` (truncate/seed) |

**Never run pytest against `nidus_core`.** The test suite uses `TEST_APP_DATABASE_URL` and `TEST_DATABASE_URL` automatically.

---

## Operational Command Center

Use these commands from the project root. Ensure your `.env` is present at the root.

### 🗄 Infrastructure (Docker)
| Goal | Command |
| :--- | :--- |
| **Start Everything** | `docker compose up -d` |
| **Start Only DB** | `docker compose up -d db` |
| **Stop Everything** | `docker compose stop` |
| **Full Wipe & Reset** | `docker compose down -v` |
| **View DB Logs** | `docker logs -f nidus-postgres` |
| **View API Logs** | `docker logs -f nidus-fastapi` |

### 🚀 Backend Development (Python/uv)
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

### 💻 Frontend Development (pnpm)
| Goal | Command |
| :--- | :--- |
| **Install Deps** | `pnpm install` |
| **Dev Mode** | `pnpm --filter nidus-frontend dev` |
| **Build Prod** | `pnpm --filter nidus-frontend build` |
| **Strict Typecheck** | `pnpm --filter nidus-frontend tsc --noEmit` |
| **Run Linter** | `pnpm --filter nidus-frontend lint` |
| **Add UI Component** | `pnpm --filter nidus-frontend dlx shadcn@latest add <component>` |
| **Clean cache** | `pnpm store prune` |

### 🧹 Maintenance & Cleanup
| Goal | Command |
| :--- | :--- |
| **Fix Line Endings** | `dos2unix infrastructure/db-init/*.sh` (If utility is installed) |
| **Prune Volumes** | `docker volume prune -f` |

---
*Developed by Isaac Granados Quesada — Principal Engineer & Computer Architect.*