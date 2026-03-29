# NIDUS: Architecture Decision Records (ADRs)

This document tracks the core architectural decisions made during the lifecycle of the NIDUS project. We follow a strictly append-only philosophy to preserve institutional memory.

---

## ADR 001: Backend Architecture and Infrastructure Setup

**Date:** 2026-03-28
**Status:** Accepted

### Context
NIDUS requires a scalable, maintainable backend architecture capable of handling multitenancy via PostgreSQL RLS. The development environment must mirror production closely to ensure Developer Experience (DX) and reliability.

### Decision
1. **Architecture:** Adopted a Modular Monolith approach utilizing Clean Architecture principles.
2. **Infrastructure:** Utilized Docker Compose with PostgreSQL 17 and FastAPI 0.110+. Database connections are strictly asynchronous utilizing `asyncpg`.
3. **Environment Management:** Selected **`uv`** (by Astral) as the primary package manager. It handles dependency injection, environment isolation, and script execution (`uv run`) to maximize speed and parity.
4. **Configuration:** Adopted `pydantic-settings` for 12-Factor App compliant environment variable management.

### Consequences
* **Positive:** High cohesion and low coupling. Frictionless local development via `uv`.
* **Negative:** Requires strict discipline in managing the `.venv` path in IDEs (Pylance).

---

## ADR 002: Multitenant Data Isolation Strategy

**Date:** 2026-03-28
**Status:** Accepted

### Context
NIDUS is a multitenant SaaS. We must ensure absolute data privacy between tenants while maintaining high database performance and simplified operational overhead.

### Decision
Adopted a **Shared Database, Shared Schema** architecture utilizing **PostgreSQL Row-Level Security (RLS)**. Isolation is enforced at the database engine level via an `organization_id` column present in all tenant-scoped tables.

### Consequences
* **Positive:** Highly scalable and efficient connection pooling. Simplified migrations via Alembic (one execution for all tenants).
* **Negative:** Requires mandatory inheritance from `TenantMixin` for all scoped entities.

---

## ADR 003: Dual-Role Database Access Strategy

**Date:** 2026-03-28
**Status:** Accepted

### Context
RLS is bypassed by superusers or table owners. To ensure isolation is strictly enforced during development and runtime, we need separate access levels.

### Decision
Implemented a **Dual-Role Connection Strategy**:
1. **`DATABASE_URL` (App User):** Restricted privileges. Forced to obey RLS policies. Used by FastAPI.
2. **`DATABASE_ADMIN_URL` (Admin User):** High privileges. Bypasses RLS. Used exclusively for Alembic migrations and maintenance.

### Consequences
* **Positive:** Guaranteed Dev/Prod parity. Accidental "God Mode" leaks in the application layer are physically impossible at the database level.

---

## ADR 004: Unified Domain Modeling via SQLModel Mixins

**Date:** 2026-03-28
**Status:** Accepted (Supersedes previous Shared Mixin drafts)

### Context
Initial attempts with separate SQLAlchemy Mixins in a `shared/` folder led to "split-brain" architecture and column assignment conflicts in SQLModel.

### Decision
1. **Consolidation:** Eliminated the `app/shared/` directory. All base logic now resides in `app/models/base.py`.
2. **Mixin Strategy:** Implemented `UUIDMixin`, `TimestampMixin`, and `TenantMixin` using **SQLModel** classes.
3. **Lazy Initialization:** Used `sa_column_kwargs` for server-side defaults (e.g., `gen_random_uuid()`) to prevent SQLAlchemy from sharing column instances across different tables.

### Consequences
* **Positive:** Zero-boilerplate models. Full Pydantic/SQLAlchemy compatibility in a single class definition.
* **Negative:** None; significantly simplified the codebase and resolved Pylance type issues.

---

## ADR 005: Naming Conventions and Domain Standardization

**Date:** 2026-03-28
**Status:** Accepted

### Context
Database naming often oscillates between plural and singular. Inconsistent naming leads to mapping complexity in ORMs like SQLModel.

### Decision
1. **Singular Naming:** All database tables follow the singular convention (`user`, `organization`, `member`, `role`) to maintain a 1:1 mapping with Python class names.
2. **Business Terminology:** Standardized on the term **`organization`** instead of `tenant` to better align with the NIDUS SaaS business domain.
3. **Directory Structure:** Organized models by domain context: `app/models/identity/` and `app/models/organization/`.

### Consequences
* **Positive:** Intuitive imports and predictable table names. Clearer business logic terminology.