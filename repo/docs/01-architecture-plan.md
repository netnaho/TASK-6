# Architecture Plan

## 1) Final architecture plan

NutriDeclare Offline Compliance System is a Docker Compose based, offline-first, role-aware compliance platform with a Vue 3 SPA frontend and a FastAPI backend. PostgreSQL stores transactional data, encrypted sensitive fields, immutable audit records, refresh token hashes, import/export metadata, and file metadata. Local disk storage stores generated PDFs, raw exports, import payloads, and revision attachments, with permission checks enforced on every download.

### Chosen stack
- Frontend: Vue 3, Vite, TypeScript, Vue Router, Pinia, Axios, Naive UI
- Backend: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2
- Database: PostgreSQL
- Auth: username/password only, JWT access and refresh tokens
- Jobs: APScheduler in-process within backend container
- Storage: local disk mounted by Docker named volume, DB metadata in PostgreSQL
- Deployment: Docker Compose only

### Architectural style
- Frontend: feature-oriented SPA with shared design system wrappers, route guards, RBAC-aware layout shells, query services, and reusable timeline/table/form modules
- Backend: layered monolith with strict separation between API, business services, repositories, models, schemas, jobs, security, and storage
- Persistence: relational schema with version tables and append-only audit log
- Files: metadata-first storage model with expiring download tokens and server-side authorization on each access

### Runtime services
- `frontend`: serves the Vite-built SPA via Nginx on port `4173`
- `backend`: FastAPI app on port `8000`, runs migrations, seed data, scheduler, and API
- `postgres`: PostgreSQL on port `5432`

### Primary product workflows
- Participant registers, logs in, completes guided health profile, creates phased nutrition plans, submits declaration packages, reviews correction requests, acknowledges feedback, resubmits, downloads permitted artifacts, and confirms acceptance
- Reviewer works queue ordered by SLA deadline, inspects package history, issues structured correction requests, reviews resubmissions, and finalizes review outputs
- Administrator manages accounts, password resets, field mappings, masking policies, import/export operations, reference data, audit queries, delivery packaging, and compliance monitoring

### Cross-cutting backend concerns
- standard API response envelope for success and errors
- centralized lifecycle validators for legal state transitions
- immutable audit service for all critical actions
- field-level encryption abstraction for sensitive profile data
- password policy, password history, account lockout, forced password change, and refresh-token hashing
- structured logging with request correlation ids
- pagination and filter objects for all list endpoints

## 7) Security design summary

### Authentication
- local username/password only
- password minimum length `12`
- must satisfy at least 3 of 4 character classes: uppercase, lowercase, digit, special
- last 5 password hashes retained and checked on change/reset
- account locked for 15 minutes after 5 failed login attempts
- access token TTL `30 minutes`
- refresh token TTL `7 days`
- refresh tokens stored hashed in PostgreSQL and rotated on refresh
- optional local CAPTCHA enabled by config flag, implemented with local challenge generation and verification only
- admin can deactivate accounts
- admin can issue offline password reset and mark `force_password_change=true`

### Authorization
- RBAC enforced in backend dependencies and service-level guards
- frontend route guards and menu filtering mirror backend permissions but never replace backend checks
- declaration lifecycle actions require both role permission and current state eligibility
- file download always checks acting user, file category, package state, token validity, and expiry

### Data protection
- sensitive profile fields encrypted at rest via backend field encryption service using AES-256-GCM and key material supplied through container environment
- encryption is abstracted behind a type-safe service so models stay persistence-focused
- passwords hashed with Argon2id
- refresh tokens hashed with SHA-256 plus server-side pepper before persistence
- audit log stores immutable action record, actor, target, old/new state, metadata checksum, and timestamp
- no stack traces in API responses; structured server logs only

### Security-relevant domain rules
- mandatory compliance alerts cannot be muted
- disabled accounts cannot authenticate or refresh
- expired download links show explicit expired messaging and require regeneration if allowed by policy
- illegal lifecycle transitions are rejected server-side even if the UI hides them

## 8) Scheduler and job design

APScheduler runs inside the backend process with singleton startup registration. Jobs are idempotent and logged to a scheduler execution table for observability.

### Scheduled jobs
- nightly search index rebuild: rebuilds denormalized local search tables for packages, plans, profiles, notifications, and audit lookups
- hourly reviewer workload stats refresh: recalculates open queue counts, overdue counts, average turnaround, and upcoming deadlines by reviewer
- cleanup expired download tokens: revokes expired tokens and marks them unavailable for file access
- cleanup old notifications: purges or archives notifications past retention policy while preserving mandatory compliance alert evidence rules

### Job protections
- advisory lock in PostgreSQL prevents duplicate execution if backend restarts overlap
- each run writes start time, end time, outcome, row counts, and error summary to job history table
- failures never crash the API process; they emit structured logs and persist failure metadata

## 9) Test strategy

### Unit tests
- pure business rules in `unit_tests/`
- fast isolated coverage for password policy, password history, lockout, token rotation rules, lifecycle transitions, correction workflow, download expiry, notification mute rules, export masking, checksum generation, version diff summaries, and permission guards

### API functional tests
- full backend HTTP coverage in `API_tests/`
- uses disposable PostgreSQL test database, seeded fixtures, and file-storage temp directory
- validates auth flows, profile CRUD, plan versioning, declaration lifecycle, reviewer corrections, delivery downloads, acceptance, notifications, import/export, admin operations, and audit queries

### Frontend verification
- implementation phase will include component/store tests for route guards, dashboard rendering, and form state logic if needed for regressions; mandatory root deliverables remain unit and API tests

## 10) Docker and startup plan

`docker compose up --build` is the single supported start command.

### Compose startup sequence
- `postgres` starts with named volume for data
- `backend` waits for PostgreSQL readiness, runs Alembic migrations automatically, seeds demo users/reference data/sample packages automatically, creates storage directories on mounted volume, starts FastAPI, then starts APScheduler during app lifespan
- `frontend` builds SPA and serves static assets via Nginx

### Named volumes
- `postgres_data` for PostgreSQL cluster data
- `file_storage` for generated files, import payloads, exports, PDFs, and delivery artifacts

### Required startup outputs
- frontend reachable in browser
- backend API reachable with seeded accounts
- demo workflows available without manual imports or env-file editing

## 11) Explicit assumptions

- The system is offline-first in the sense that all dependencies are local-only at runtime; it does not rely on any external SaaS or cloud service.
- Generated PDFs will be produced locally by a backend PDF generation library and stored on the mounted local volume.
- Search index rebuild refers to a local PostgreSQL-backed denormalized search table strategy, not Elasticsearch or any external engine.
- Sensitive-field encryption will be implemented in the backend layer rather than PostgreSQL extension-based encryption to avoid non-portable DB extension assumptions while still delivering real encryption.
- Default download link expiry is 72 hours, with administrator-configurable shorter or longer policy bounds implemented in application settings.
