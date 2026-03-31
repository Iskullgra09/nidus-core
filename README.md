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
| **Persistence** | Async SQLModel + PostgreSQL 18 AIO Ready |
| **Isolation** | Dual-Role Security (Restricted Session User vs. Migration Admin) |
| **Optimization** | Partial Unique Indexes + GIN Indexed JSONB Scopes |
| **Auditing** | Global Soft-Delete Infrastructure & Temporal Mixins |

---

## Project Roadmap (Updated 2026)

### Completed Milestones
| Phase | Goal | Achievements |
| :--- | :--- | :--- |
| **0** | **Infrastructure** | `uv` orchestration, Dockerized PostgreSQL 17, Monorepo logic. |
| **1** | **Data Engine** | RLS Policies, Consolidated Baseline Migration, Security Setup. |
| **2** | **Identity** | JWT stateless auth, BCrypt hashing, Atomic Tenant Onboarding. |
| **3.1**| **Infrastructure Evolution** | Soft-Delete Mixins, Partial Indexes, SQLModel Refactor. |

### Upcoming Phases
#### **Phase 3: RBAC & Governance** (Current)
- [x] **Hierarchical Scopes:** Implementation of `module:resource:action` namespacing.
- [x] **JSONB Scopes:** High-performance GIN-indexed permissions in `Role` table.
- [ ] **Permission Guard:** FastAPI Dependency-based scope verification.
- [ ] **Member Invitations:** Secure join-token flow for new tenant users.

#### **Phase 4: Frontend & Scaling** (Next.js 15)
- [ ] **Edge Resolution:** Tenant detection via Next.js Middleware & Edge Config.
- [ ] **PPR Dashboards:** Partial Prerendering for ultra-fast tenant shells.
- [ ] **Connection Pooling:** PgBouncer integration for 100k+ tenant scaling.
- [ ] **UUIDv7 Migration:** Transition to sequential UUIDs for index locality.

---

## Quick Start

1. **Synchronize Environment:**
    ```powershell
    uv sync
    ```

2. **Orchestrate Infrastructure:**
    ```powershell
    docker compose up -d
    ```

3. **Baseline Evolution:**
    ```powershell
    uv run alembic upgrade head
    ```

4. **Verify Integrity (RLS & Logic):**
    ```powershell
    uv run pytest
    ```

---
*Developed by Isaac Granados Quesada — Principal Engineer & Computer Architect.*