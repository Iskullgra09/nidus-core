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
#### **Phase 4: Frontend & Scaling** (Next.js 15)
- [ ] **Edge Resolution:** Tenant detection via Next.js Middleware.
- [ ] **PPR Dashboards:** Partial Prerendering for tenant shells.
- [ ] **Connection Pooling:** PgBouncer integration for 100k+ scaling.

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