# NIDUS: Architecture Decision Records (ADRs)

This document tracks the core architectural decisions made during the lifecycle of the NIDUS project. We follow a strictly append-only philosophy to preserve institutional memory.

---

## ADR 001: Backend Architecture and Infrastructure Setup

**Date:** 2026-03-28
**Status:** Accepted

### Context
NIDUS requires a scalable, maintainable backend architecture capable of handling multitenancy via PostgreSQL RLS. The development environment must mirror production closely to ensure Developer Experience (DX) and reliability.

### Decision
1. **Architecture:** Adopted a Modular Monolith approach utilizing Clean Architecture principles. Modules (e.g., `tenant`, `identity`) are strictly separated into `domain`, `application`, `infrastructure`, and `presentation` layers.
2. **Infrastructure:** Utilized Docker Compose with PostgreSQL 17 (Alpine) and FastAPI 3.12+. Database connections are strictly asynchronous utilizing `asyncpg`.
3. **Environment Management:** Selected `uv` (by Astral) as the Python package manager and virtual environment resolver to maximize CI/CD and local DX speed.
4. **Configuration:** Adopted `pydantic-settings` for 12-Factor App compliant environment variable management, ensuring type safety and fail-fast validation on startup.

### Consequences
* **Positive:** High cohesion and low coupling. Easy to extract microservices in the future. Strong type safety for configuration. Frictionless local development environment via `uv`.
* **Negative:** Slight initial overhead in creating directories and mapping between layer boundaries (e.g., Domain Models vs. SQLAlchemy Models).

---

## ADR 002: Multitenant Data Isolation Strategy

**Date:** 2026-03-28
**Status:** Accepted

### Context
NIDUS is a multitenant SaaS. We must ensure absolute data privacy between tenants while maintaining high database performance and simplified operational overhead during schema migrations.

### Decision
Adopted a **Shared Database, Shared Schema** architecture utilizing **PostgreSQL Row-Level Security (RLS)**. All tenant data will reside in the same tables, isolated strictly by a `tenant_id` column and enforced by database-level security policies.

### Consequences
* **Positive:** Highly scalable. Connection pooling (`asyncpg`) remains extremely efficient. Alembic schema migrations only need to be executed once per deployment across the entire platform.
* **Negative:** Requires rigorous engineering discipline. Every table must have RLS enabled and policies meticulously defined to prevent catastrophic cross-tenant data leaks.