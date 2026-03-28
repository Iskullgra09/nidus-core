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
| **Database** | Async SQLAlchemy 2.0 + Alembic Migrations |
| **Security** | Dual-Role Access (Restricted App User vs. God-Mode Admin) |
| **Dependency Mgmt** | `uv` by Astral (Lightning-fast resolver) |
| **Testing** | `pytest` + `pytest-asyncio` with 100% RLS verification |

---

## Project Roadmap

### Completed Milestones
| Phase | Goal | Key Achievements |
| :--- | :--- | :--- |
| **0** | **Infrastructure** | Monorepo setup, `uv` config, Docker Compose orchestration. |
| **1** | **Data Engine** | `Tenant` model, RLS Policy implementation, Restricted user setup. |

### Upcoming Phases
- [ ] **Phase 2: Identity & Access Management**
  - [ ] `User` and `TenantMember` domain models.
  - [ ] Password hashing & JWT integration.
  - [ ] RBAC (Role-Based Access Control) logic.
- [ ] **Phase 3: Tenant Middleware**
  - [ ] Automatic `tenant_id` injection from JWT to Postgres Session.
- [ ] **Phase 4: Dashboard Shell**
  - [ ] Next.js 15 App Router foundation & UI Components.

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
    pytest -v
    ```

---
*Developed by Isaac Granados Quesada — Principal Engineer & Computer Architect.*