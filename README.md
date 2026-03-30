# Nidus Core 
**The foundation for modern, scalable, and secure SaaS applications.**

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-336791.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Nidus is an enterprise-ready monorepo designed to serve as the backbone for scalable SaaS products. It implements **Clean Architecture**, **Modular Monolith** patterns, and hardware-level data isolation using **PostgreSQL Row-Level Security (RLS)**.

---

## Architectural Core

| Feature | Implementation |
| :--- | :--- |
| **Multitenancy** | Shared Schema with PostgreSQL RLS (Row-Level Security) |
| **Database** | Async SQLAlchemy 2.0 + NullPool for Windows Stability |
| **Security** | Dual-Role Access (Restricted App User vs. God-Mode Admin) |
| **Identity** | JWT-based stateless auth with injected Tenant DNA |
| **Testing** | `pytest` + `pytest-asyncio` with 100% RLS verification |

---

## Project Roadmap

### Completed Milestones
| Phase | Goal | Key Achievements |
| :--- | :--- | :--- |
| **0** | **Infrastructure** | Monorepo setup, `uv` config, Docker Compose orchestration. |
| **1** | **Data Engine** | `Tenant` model, RLS Policy implementation, Restricted user setup. |
| **2** | **Identity & Multitenancy** | Atomic Onboarding, Bcrypt hashing, JWT integration, and `/me` validation. |

### Upcoming Phases
- [ ] **Phase 3: RBAC & Permission Scopes**
  - [ ] Granular Permissions system (Scopes).
  - [ ] Dynamic Role assignment per Organization.
  - [ ] Invitation system for new Members.
- [ ] **Phase 4: Dashboard Shell**
  - [ ] Next.js 15 App Router foundation & UI Components.
  - [ ] Shared Component Library (Tailwind + Shadcn).

---

## 🛠️ Quick Start

1. **Environment Setup:**
    ```bash
    # 1. Sync dependencies and environment
    uv sync

    # 2. Start infrastructure (Database)
    docker compose up -d

    # 3. Apply all database migrations
    alembic upgrade head

    # 4. Verify RLS and Security via test suite
    uv run pytest
    ```

---
*Developed by Isaac Granados Quesada — Principal Engineer & Computer Architect.*