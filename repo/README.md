# NutriDeclare Offline Compliance System

NutriDeclare Offline Compliance System is an offline-first compliance platform for workplace wellness workflows. It supports participant, reviewer, and administrator roles with local authentication, guided health profiles, phased nutrition planning, declaration lifecycle control, corrections, deliveries, audit logging, import/export tooling, and in-process scheduled maintenance jobs.

## Start Command

```bash
docker compose up --build
```

No manual `.env` creation, DB import, or interactive setup is required.

## Service Addresses

- Frontend UI: `http://localhost:4173`
- Backend API: `http://localhost:8000`
- Backend health: `http://localhost:8000/health`
- PostgreSQL: `localhost:55432`

## Demo Accounts

- Participant
  - username: `participant_demo`
  - password: `Participant#2026`
- Reviewer
  - username: `reviewer_demo`
  - password: `Reviewer#2026`
- Administrator
  - username: `admin_demo`
  - password: `Admin#2026Secure`

## Project Overview

- Frontend: Vue 3 + Vite + TypeScript + Vue Router + Pinia + Axios + Naive UI
- Backend: FastAPI + SQLAlchemy + Alembic + Pydantic v2
- Database: PostgreSQL
- Auth: local username/password only with JWT access and refresh flow
- Scheduling: APScheduler running in-process in backend container
- Storage: local Docker volume for files plus PostgreSQL metadata
- Deployment: Docker Compose only

## Architecture Summary

### Backend
- `backend/app/api/` - route handlers and dependency wiring
- `backend/app/core/` - config, constants, logging, exception handling, response envelope
- `backend/app/db/` - engine, sessions, seed bootstrap
- `backend/app/models/` - ORM entities
- `backend/app/repositories/` - database access layer
- `backend/app/services/` - business workflows and lifecycle rules
- `backend/app/security/` - password policy, JWT, encryption, CAPTCHA, RBAC helpers
- `backend/app/jobs/` - scheduled maintenance jobs
- `backend/app/storage/` - file storage, PDF generation, checksum logic
- `backend/app/utils/` - timestamps, diff summaries, pagination helpers

### Frontend
- `frontend/src/layouts/` - authenticated and unauthenticated shells
- `frontend/src/router/` - route map and role-based guards
- `frontend/src/stores/` - auth, notifications, shell state, preferences
- `frontend/src/api/` - modular backend integration layer
- `frontend/src/components/` - reusable tables, badges, timelines, forms, and delivery panels
- `frontend/src/views/` - role-specific pages for participants, reviewers, administrators, and auth/shared flows

## Directory Structure

```text
.
|-- backend/
|-- frontend/
|-- unit_tests/
|-- API_tests/
|-- docs/
|-- docker-compose.yml
|-- run_tests.sh
`-- README.md
```

## Automatic Startup Behavior

- PostgreSQL starts with a named persistent volume
- Backend waits for PostgreSQL health
- Backend runs Alembic migrations automatically on startup
- FastAPI app seeds demo data automatically during app lifespan if the database is empty
- APScheduler starts automatically with the backend process
- Frontend starts on Nginx and proxies `/api/*` requests to the backend

## Verification Steps

### 1. Verify startup
- Run `docker compose up --build`
- Open `http://localhost:4173`
- Confirm the login page loads
- Open `http://localhost:8000/health` and confirm `{"status":"ok"}`

### 2. Verify participant workflow
- Sign in as `participant_demo`
- Open Health Profile and save an update
- Open Nutrition Plans and edit or create a plan version
- Open Declarations and create or review a package
- Submit a draft declaration
- Open package detail and confirm status badge and due date display

### 3. Verify reviewer workflow
- Sign in as `reviewer_demo`
- Open Review Queue and confirm assigned packages are listed
- Open a package and submit a correction request

### 4. Verify correction flow
- Sign back in as `participant_demo`
- Open the corrected declaration
- Acknowledge and resubmit the correction

### 5. Verify administrator workflow
- Sign in as `admin_demo`
- Open Users to disable or reset an account
- Open Audit Trail to inspect immutable audit entries
- Open Import & Export to create mappings, policies, and exports
- Open Settings and update local runtime controls

### 6. Verify downloads and acceptance
- As a participant, upload or view delivery artifacts from a package detail page
- Generate a secure download link
- Confirm acceptance for a delivered package

## How To Run Tests

Run the full unit and API suite with Docker Compose:

```bash
./run_tests.sh
```

The script:
- starts PostgreSQL if needed
- creates a dedicated `nutrideclare_test` database automatically
- runs `pytest` for `unit_tests/` and `API_tests/` inside the backend container

## Key Business Rules

- password minimum length is 12 characters
- password must satisfy at least 3 of 4 character classes
- new password cannot match any of the last 5 passwords
- accounts lock for 15 minutes after 5 failed login attempts
- access token TTL is 30 minutes
- refresh token TTL is 7 days and is stored hashed in PostgreSQL
- declaration states are strictly enforced: `draft`, `submitted`, `withdrawn`, `corrected`, `voided`
- illegal lifecycle transitions are rejected server-side
- reviewer correction requests preserve version history and participant acknowledgement/resubmission flow
- mandatory compliance alerts cannot be muted
- download links expire by default after 72 hours
- file access requires both valid token state and package permission checks
- audit logs are append-only and hash-linked for tamper evidence

## Security Notes

- authentication is fully local-only with no external identity providers
- sensitive profile fields use hybrid encryption: app-layer AES-256-GCM plus PostgreSQL `pgcrypto` encryption at rest
- passwords use Argon2id hashing
- refresh tokens and download tokens are stored hashed
- RBAC is enforced in backend APIs and mirrored in frontend navigation and route guards
- standardized JSON error envelopes avoid leaking stack traces to clients

## Database-Side Encryption

- PostgreSQL `pgcrypto` is enabled by migration (`enable_pgcrypto_db_encryption`) and used to encrypt `participant_profiles.encrypted_payload` in-database.
- The service still applies AES-256-GCM in the application before persistence for defense-in-depth.
- Runtime controls:
  - `DB_ENCRYPTION_ENABLED=true|false` (default `true`)
  - `DB_ENCRYPTION_KEY=<passphrase>` (recommended)
  - fallback key: `ENCRYPTION_KEY` when `DB_ENCRYPTION_KEY` is unset
- Key management guidance:
  - provision `DB_ENCRYPTION_KEY` via environment variables or secret manager
  - rotate with a controlled migration/re-encryption window
  - never keep production keys in source-controlled `.env` files

## Test Coverage Included

### Unit tests
- password policy
- password history
- lockout
- token logic
- lifecycle transitions
- correction workflow
- download token expiry
- notification mute rules
- export masking
- checksum generation
- version diff summaries
- permission checks

### API tests
- registration/login/lockout
- refresh flow
- forced password change
- profile CRUD
- plan CRUD and versions
- declaration lifecycle
- reviewer correction workflow
- delivery download valid vs expired
- acceptance confirmation
- notifications and mute settings
- import/export
- admin disable/reset
- audit log query
