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

### Completed Milestones
| Phase | Goal | Achievements |
| :--- | :--- | :--- |
| **1** | **Data Engine** | RLS Policies, Baseline Migration, Security Setup. |
| **2** | **Identity Base** | JWT stateless auth, BCrypt, Atomic Tenant Onboarding. |
| **3** | **RBAC & Governance** | Hierarchical Scopes, GIN-indexed Role Scopes, UUIDv7. |
| **3.5**| **Reliability Layer**| Global Exception Handlers, 100% i18n support, Pydantic 422 Translation. |
| **3.6**| **Lifecycle & Mail** | Asynchronous email dispatch (`aiosmtplib`), Secure Invitation Lifecycle, Password Recovery. |
| **3.7**| **The Data Standard**| O(1) Keyset Pagination via UUIDv7, Dynamic Pydantic-to-SQL Filtering Engine, Cascading Soft-Deletes. |

### In Progress / Upcoming
#### **Phase 4: Frontend Core & UI Architecture** (Next.js 16)
- [x] **Gateway Proxy:** Edge routing and JWT session validation (`src/proxy.ts`).
- [x] **Design System:** Shadcn "Nova" + Tailwind v4 + OKLCH for predictable, high-density SaaS UI.
- [x] **Type-Safe Forms:** Zod (pinned to v3 for ecosystem stability) + React Hook Form.
- [x] **Authentication Pipeline:** Login Server Actions with HttpOnly cookie generation.
- [ ] **The Happy Path:** Minimalist Command-Driven Top-Bar, Org Switcher, and secure Logout.
- [ ] **Frontend i18n:** Localization pipeline integration for UI components and client-side schemas.
- [ ] **Secondary Auth Flows:** Registration, Atomic Onboarding, and Stateless Password Recovery.
- [ ] **Data Fetching:** SWR or React 19 `use` cache for fetching and streaming tenant data.

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
| **Run Migrations** | `uv run alembic upgrade head` |
| **Create Migration** | `uv run alembic revision --autogenerate -m "description"` |
| **Run Seed Script** | `uv run seed.py ` |
| **Run Seed Script on Docker** | `docker exec -it nidus-fastapi python app/core/seed.py` |
| **Run API Locally** | `uv run fastapi dev app/main.py` |
| **Run Tests** | `uv run pytest` |

### 💻 Frontend Development (pnpm)
| Goal | Command |
| :--- | :--- |
| **Install Deps** | `pnpm install` |
| **Dev Mode** | `pnpm --filter nidus-frontend dev` |
| **Build Prod** | `pnpm --filter nidus-frontend build` |
| **Clean cache** | `pnpm store prune` |

### 🧹 Maintenance & Cleanup
| Goal | Command |
| :--- | :--- |
| **Fix Line Endings** | `dos2unix infrastructure/db-init/*.sh` (If utility is installed) |
| **Prune Volumes** | `docker volume prune -f` |

---
*Developed by Isaac Granados Quesada — Principal Engineer & Computer Architect.*