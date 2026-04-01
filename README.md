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

### ✅ Completed Milestones
| Phase | Goal | Achievements |
| :--- | :--- | :--- |
| **1** | **Data Engine** | RLS Policies, Baseline Migration, Security Setup. |
| **2** | **Identity Base** | JWT stateless auth, BCrypt, Atomic Tenant Onboarding. |
| **3** | **RBAC & Governance** | Hierarchical Scopes, GIN-indexed Role Scopes, UUIDv7. |
| **3.1**| **Identity Flow A** | Secure Invitation System (Part A: Creation & RLS). |

### 🛠️ In Progress / Upcoming
#### **Phase 3.5: Reliability & Globalization** (Current)
- [ ] **Global Error Handling:** Unified Exception Handlers for consistent API contracts.
- [ ] **i18n Engine:** Multi-language support (Accept-Language) for business errors.
- [ ] **Invitation Flow B:** Public token validation & secure account activation.

#### **Phase 4: Frontend & Scaling** (Next.js 15)
- [ ] **Edge Resolution:** Tenant detection via Next.js Middleware.
- [ ] **PPR Dashboards:** Partial Prerendering for tenant shells.
- [ ] **Connection Pooling:** PgBouncer integration for 100k+ scaling.

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