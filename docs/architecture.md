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

---

## ADR 006: Modular Architecture and API v1 Layering

**Date:** 2026-03-28
**Status:** Accepted

### Context
To ensure NIDUS Core remains scalable and allows multiple developers to collaborate without merge conflicts, the `main.py` file must be kept clean of business logic and extensive route definitions.

### Decision
1. **Routing Pattern:** Implemented `APIRouter` with a centralized orchestrator in `app/api/v1/api.py`.
2. **Directory Structure:** Adopted a clear separation of concerns:
   - `endpoints/`: Route controllers (Entry points).
   - `schemas/`: Pydantic models for request/response validation.
   - `services/`: Pure business logic (to be implemented next).
3. **API Versioning:** All current logic moved under the `/api/v1` prefix to allow future iterations without breaking existing contracts.

### Consequences
* **Positive:** Highly organized code, easier unit testing, and allows for modular growth of the Core.
* **Negative:** Slightly increases the initial number of files and the complexity of relative imports.

---

## ADR 007: Security and Identity (Bcrypt & JWT)

**Date:** 2026-03-29
**Status:** Accepted

### Context
Initial security relied on `passlib`, which caused compatibility issues with modern `bcrypt` versions (AttributeError) and had a 72-byte limitation that wasn't explicitly handled in our service layer.

### Decision
1. **Direct Hashing:** Abandoned `passlib` in favor of the direct `bcrypt` library for better performance and 2026 compatibility.
2. **Deterministic Truncation:** Implemented explicit `.encode('utf-8')[:72]` truncation in `hash_password` and `verify_password` to prevent Bcrypt overflow errors while maintaining maximum security.
3. **JWT Context:** Adopted JWT (HS256) for authentication, embedding both `sub` (User UUID) and `org_id` (Organization UUID) to facilitate stateless multitenancy.

### Consequences
* **Positive:** Robust, error-free hashing. JWTs now carry the "Tenant DNA" required for RLS.
* **Negative:** Manual byte management in Python, but it provides full control over the hashing process.

---

## ADR 008: Atomic Tenant Onboarding Service

**Date:** 2026-03-29
**Status:** Accepted

### Context
Creating an organization involves multiple related entities (Org, Admin User, Role, Membership). Doing this in separate API calls is prone to partial failures and data inconsistency.

### Decision
Implemented a **`TenantService.create_onboarding`** method that:
1. Executes all inserts within a single database transaction.
2. Uses a "Get or Create" pattern for system roles (e.g., "Admin").
3. Automatically establishes the initial `Member` link between the first user and the new organization.

### Consequences
* **Positive:** Guaranteed consistent initial state for every new client. Simplified frontend integration (one form, one request).

---

## ADR 009: RLS Bypass for Authentication & Onboarding

**Date:** 2026-03-29
**Status:** Accepted

### Context
PostgreSQL RLS blocks all rows if `app.current_organization_id` is not set. This creates a "chicken and egg" problem during Login and Onboarding, where the system needs to read data to identify the tenant.

### Decision
1. **Conditional Policy:** Updated RLS policies to allow `SELECT` operations on identity tables (`user`, `organization`, `member`, `role`) if the session variable is empty: 
   `USING (organization_id::text = current_setting('app.current_organization_id', TRUE) OR current_setting('app.current_organization_id', TRUE) = '')`.
2. **Explicit Session Reset:** Forced `SET LOCAL app.current_organization_id = ''` at the start of the `AuthService.authenticate` method to ensure a clean, global context for credentials verification.

### Consequences
* **Positive:** Fully autonomous login flow without manual database intervention.
* **Negative:** Requires strict discipline to ensure session variables are correctly set immediately after authentication.

---

## ADR 010: API Boundary Standardization (Schemas & Generic Responses)

**Date:** 2026-03-30
**Status:** Accepted

### Context
Returning raw SQLAlchemy models or unformatted dictionaries directly to the client exposes internal database structures (like password hashes) and creates an inconsistent contract for frontend consumers.

### Decision
1. **Horizontal Slicing for Schemas:** Organized Pydantic models into `app/schemas/requests/` (strict validation for incoming data) and `app/schemas/responses/` (safe representation of outgoing data) rather than grouping them vertically by domain.
2. **Generic Wrapper:** Implemented a `GenericResponse[T]` model to ensure all API endpoints return a predictable shape: `{ "status": "success", "message": null, "data": { ... } }`.
3. **Explicit Schema Init:** Decided to keep all `__init__.py` files inside the schema directories explicitly empty to prevent circular imports and optimize memory loading.

### Consequences
* **Positive:** Strict data hiding, predictable API contracts for frontend developers, and clear boundaries between Domain Models (SQLModel) and DTOs (Data Transfer Objects).
* **Negative:** Requires slightly more boilerplate (creating two schemas for almost every entity).

---

## ADR 011: Automated Testing Strategy for RLS Isolation

**Date:** 2026-03-30
**Status:** Accepted

### Context
Testing a multitenant system with PostgreSQL RLS requires verifying that restricted users cannot access other tenants' data. Using a superuser for tests would bypass RLS, leading to "false positive" results.

### Decision
1. **Dual-Engine Setup:** Implemented two distinct engines in `conftest.py`:
   - `admin_engine`: Uses `nidus_admin` credentials. Bypasses RLS for `TRUNCATE` and `SEED` operations.
   - `app_engine`: Uses `nidus_app_user` credentials. Strictly follows RLS policies. Used for all API integration tests.
2. **Context Bypass for Verification:** To verify DB state during tests without using the admin engine, we utilize the `SET LOCAL app.current_organization_id = ''` bypass within an explicit `session.begin()` block.

### Consequences
* **Positive:** Guaranteed validation of security policies. Tests fail if RLS is misconfigured.
* **Negative:** Slightly more complex `conftest.py` setup.

---

## ADR 012: Connection Management and Windows Stability (NullPool)

**Date:** 2026-03-30
**Status:** Accepted

### Context
Using `asyncpg` on Windows with the default SQLAlchemy connection pool leads to `RuntimeError: Event loop is closed` and `AttributeError: 'NoneType' object has no attribute 'send'`. This happens because the pool tries to maintain "zombie" connections after the `pytest-asyncio` loop is destroyed.

### Decision
1. **NullPool Implementation:** Adopted `sqlalchemy.pool.NullPool` for all test engines. This forces each session to open and close a real physical connection, preventing persistent sockets from being tied to closed event loops.
2. **Session-Scoped Loop:** Forced a single `event_loop` fixture with "session" scope to maintain a stable heart-beat for all asynchronous tests.

### Consequences
* **Positive:** 100% stability on Windows environments. Zero "zombie" connection errors.
* **Negative:** Minor performance overhead due to lack of connection pooling (negligible for the current test suite size).

---

## ADR 013: Soft Delete and Partial Unique Constraints (Refined)

**Date:** 2026-03-31
**Status:** Accepted 

### Context
Standard unique constraints in PostgreSQL prevent the re-use of identifiers (emails, slugs) even after a record is logically deleted. In a SaaS, a tenant should be able to re-register a deleted slug without data conflicts.

### Decision
1. **Mechanism:** Implemented `SoftDeleteMixin` using `sa_type` to ensure SQLModel correctly clones the column instance across multiple tables.
2. **Uniqueness:** Replaced Python-level `unique=True` with **PostgreSQL Partial Unique Indexes**.
   - Example: `CREATE UNIQUE INDEX ... WHERE (deleted_at IS NULL)`.
3. **Efficiency:** Adopted the `select_active` helper pattern to standardize `is_(None)` filtering across all business services.

### Consequences
* **Positive:** Enables account re-registration. Optimized index performance as deleted rows are excluded from the unique constraint.
* **Negative:** Requires manual index definitions in Alembic migrations as autogenerate does not natively detect `postgresql_where`.

---

## ADR 014: Hierarchical Scopes and JSONB Authorization

**Date:** 2026-03-31
**Status:** Accepted

### Context
Static roles (Admin/User) are insufficient for complex SaaS requirements. We need a granular permission system that supports hierarchical scoping and high-performance checks without expensive table joins.

### Decision
1. **Scope Format:** Adopted a hierarchical string pattern: `module:resource:action` (e.g., `identity:user:write`).
2. **Storage:** Scopes are stored as a **JSONB array** directly in the `role` table.
3. **Indexing:** Implemented a **GIN Index** with `jsonb_path_ops` on the `scopes` column to enable sub-millisecond containment queries (`@>`).
4. **Inheritance:** "Write" implies "Read" logic is handled at the Application Layer (FastAPI Dependencies) to maintain a simple and predictable database schema.

### Consequences
* **Positive:** Lightning-fast authorization checks (zero joins). Extremely flexible custom roles per tenant.
* **Negative:** Requires strict adherence to the `NidusScope` Enum to prevent string drift in the database.

---

## ADR 015: Sequential UUID Generation (UUIDv7)

**Date:** 2026-03-31
**Status:** Accepted

### Context
Using standard completely random UUIDs (UUIDv4) as primary keys in a rapidly growing multitenant database causes severe performance degradation over time. Because the IDs are not sequential, every new insert forces PostgreSQL to write to random locations within its B-Tree indexes, leading to massive page fragmentation, high disk I/O, and bloated memory usage.

### Decision
1. **Standard Adoption:** Adopted **UUIDv7** (RFC 9562) as the standard primary key format for all new database records.
2. **Implementation:** Integrated the `uuid6` Python library to generate UUIDv7.
3. **Architecture:** Wrapped the generation in a strictly typed adapter function (`generate_uuid7()`) injected into the `default_factory` of the `UUIDMixin`.

### Consequences
* **Positive:** UUIDv7 includes a 48-bit timestamp prefix, making the IDs naturally sortable by creation time. This guarantees sequential inserts, keeping PostgreSQL B-Tree indexes perfectly compact, cache-friendly, and lightning-fast at any scale.
* **Negative:** Requires an external library (`uuid6`) as Python 3.12 does not support UUIDv7 natively in its standard library.

---

## ADR 016: Secure Invitation Workflow

**Date:** 2026-04-01
**Status:** Accepted

### Context
Adding users directly to an organization requires sensitive data (passwords) and bypasses consent. We need a way to invite external users while maintaining RLS isolation and preventing "ghost" users from polluting the database.

### Decision
1. **Model:** Created an `Invitation` table to store pending invites with a unique, high-entropy token (`uuid4().hex`).
2. **Security:** The table is protected by PostgreSQL RLS using the `organization_id` context.
3. **Validity:** Implemented a 7-day expiration policy and a state-check (`is_accepted`) to prevent token reuse.
4. **Endpoint Protection:** Used `ScopeGuard(NidusScope.MEMBER_WRITE)` to ensure only authorized actors can issue invites.

### Consequences
* **Positive:** Decouples user creation from organization linkage. Ensures auditability of who invited whom.
* **Negative:** Adds a step to the onboarding flow (Invite -> Accept -> Register).