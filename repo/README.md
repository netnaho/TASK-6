# NutriDeclare Offline Compliance System

**Project Type: fullstack**

NutriDeclare Offline Compliance System is an offline-first **fullstack** compliance platform for workplace wellness workflows. It ships a FastAPI backend, a Vue 3 frontend, and a PostgreSQL database wired together exclusively through Docker Compose. It supports participant, reviewer, and administrator roles with local authentication, guided health profiles, phased nutrition planning, declaration lifecycle control, corrections, deliveries, audit logging, import/export tooling, and in-process scheduled maintenance jobs.

Everything — backend, frontend build, database, and tests — runs inside Docker containers. No host-side package managers, runtime installers, or manual database setup are required; Docker Compose handles dependency provisioning and schema creation end-to-end.

## Quick Start (Deterministic Demo Mode)

Launch the full fullstack stack with deterministic, explicitly documented demo accounts and a single command:

```bash
docker-compose -f docker-compose.demo.yml up --build
```

Equivalent modern form (both are supported):

```bash
docker compose -f docker-compose.demo.yml up --build
```

This uses the committed `.compose.demo.env` file, which sets `ALLOW_INSECURE_DEV_MODE=true` so placeholder secrets are accepted, seeds deterministic demo users, and serves the frontend at `http://localhost:4173` and the backend at `http://localhost:8000`. Demo mode is strictly for local exploration and must never be used in production.

### Demo Credentials (all roles)

Every role is seeded with the exact credentials below on first boot in demo mode. Use them directly to sign in.

| Role          | Username (login) | Email (on account)         | Password            |
| ------------- | ---------------- | -------------------------- | ------------------- |
| Participant   | `participant_demo` | `participant@example.local` | `Participant#2026`  |
| Reviewer      | `reviewer_demo`    | `reviewer@example.local`    | `Reviewer#2026`     |
| Administrator | `admin_demo`       | `admin@example.local`       | `Admin#2026Secure`  |

These exact credentials are defined in `.compose.demo.env` and match the test fixtures in `.compose.test.env`, so they are stable across reboots of the demo stack.

## Production-Style Startup (Randomized Secrets)

For local installs that behave like a real deployment — randomized secrets, no demo users, fail-fast on placeholder values — use the bootstrap wrapper:

```bash
./start.sh
```

`./start.sh` auto-generates a local gitignored `.compose.env` with randomized database, JWT, refresh, CAPTCHA, and encryption secrets via `./init-db.sh`, then runs `docker compose up --build`. Re-running it simply brings the stack up against the existing `.compose.env`.

To seed randomized demo accounts on first boot in this mode:

```bash
./start.sh --with-demo-data
```

Advanced manual bootstrap is still supported:

```bash
cp .compose.example.env .compose.env
# replace every placeholder with strong site-local secrets, then:
docker-compose up --build
```

`docker-compose up --build` (equivalently `docker compose up --build`) requires a real `.compose.env`. The committed `.compose.example.env` is a template only and refuses to boot as-is. If an older `.compose.env` triggers Compose warnings like `The "X" variable is not set`, regenerate it with `./init-db.sh --force`. If PostgreSQL was already initialized with different credentials, recreate its data volume so the container and database passwords stay aligned.

## Service Addresses

- Frontend UI: `http://localhost:4173`
- Backend API root: `http://localhost:8000`
- Backend API v1 prefix: `http://localhost:8000/api/v1`
- Backend health: `http://localhost:8000/health`
- PostgreSQL: `localhost:55432` (username `nutrideclare`, database `nutrideclare`)

## Verification Steps

### 1. Verify startup
- Launch the stack: `docker-compose -f docker-compose.demo.yml up --build` (demo) or `./start.sh` (production-style).
- Open `http://localhost:4173` and confirm the login page loads.
- Open `http://localhost:8000/health` and confirm the response body is `{"status":"ok"}`.

### 2. Verify API health and login with curl

Health probe (no auth required):

```bash
curl -sS http://localhost:8000/health
# expected: {"status":"ok"}
```

Participant login (demo mode):

```bash
curl -sS -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"participant_demo","password":"Participant#2026"}'
```

The response envelope looks like `{"success":true,"message":"Login successful","data":{"access_token":"...","refresh_token":"...","token_type":"bearer",...}}`.

Authenticated identity probe using the access token from the previous step:

```bash
ACCESS_TOKEN="<paste access_token here>"
curl -sS http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

Reviewer and administrator logins use the same endpoint with `reviewer_demo` / `Reviewer#2026` and `admin_demo` / `Admin#2026Secure` respectively.

### 3. Verify participant workflow
- Sign in as `participant_demo` / `Participant#2026`.
- Open Health Profile and save an update.
- Open Nutrition Plans and edit or create a plan version.
- Open Declarations and create or review a package.
- Submit a draft declaration.
- Open package detail and confirm the status badge and due date display.

### 4. Verify reviewer workflow
- Sign in as `reviewer_demo` / `Reviewer#2026`.
- Open Review Queue and confirm assigned packages are listed.
- Open a package and submit a correction request.

### 5. Verify correction flow
- Sign back in as `participant_demo`.
- Open the corrected declaration.
- Acknowledge and resubmit the correction.

### 6. Verify administrator workflow
- Sign in as `admin_demo` / `Admin#2026Secure`.
- Open Users to disable or reset an account.
- Open Audit Trail to inspect immutable audit entries.
- Open Import & Export to create mappings, policies, and exports.
- Open Settings and update local runtime controls.

### 7. Verify downloads and acceptance
- As the reviewer or administrator, publish a delivery artifact and optionally restrict it by role.
- Generate a secure download link for either the participant or your own session.
- As the participant, download the delivered package and confirm acceptance.

## Project Overview

- **Project type:** fullstack
- Frontend: Vue 3 + Vite + TypeScript + Vue Router + Pinia + Axios + Naive UI
- Backend: FastAPI + SQLAlchemy + Alembic + Pydantic v2
- Database: PostgreSQL
- Auth: local username/password only with JWT access and refresh flow
- Scheduling: APScheduler running in-process in the backend container
- Storage: local Docker volume for files plus PostgreSQL metadata
- Deployment: Docker Compose only — no host-side package managers required

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
|-- docker-compose.yml
|-- docker-compose.demo.yml
|-- docker-compose.test.yml
|-- start.sh
|-- run_tests.sh
`-- README.md
```

## Automatic Startup Behavior

- PostgreSQL starts with a named persistent volume.
- Backend waits for PostgreSQL health.
- Backend runs Alembic migrations automatically on startup.
- FastAPI app seeds demo data automatically during app lifespan if the database is empty and `SEED_DEMO_DATA=true`.
- APScheduler starts automatically with the backend process.
- Frontend is served by Nginx in the `frontend` container and proxies `/api/*` to the backend.

## How To Run Tests

Run the full backend + frontend test suite in one Docker-contained command from a fresh clone (no host `python`, `node`, `npm`, or `pip` required):

```bash
./run_tests.sh
```

The script:
- uses a dedicated isolated Compose project (`nutrideclare-tests`) for the backend test stack so your main dev containers are not touched.
- spins up PostgreSQL, builds the backend image, and executes `pytest` for `unit_tests/` and `API_tests/` **inside the backend container** (no host Python is used; env parsing and `DATABASE_URL` construction run inside the container).
- executes frontend unit tests (Vitest + Vue Test Utils + jsdom) in a disposable `node:22-alpine` container (no host Node or npm is required).
- tears down all test containers and volumes on exit via a cleanup trap, even on failure.
- exits non-zero on any failure so CI gates correctly.

### Frontend unit test entry points

Frontend unit tests (Vitest + Vue Test Utils + jsdom) are executed automatically by `./run_tests.sh` inside a disposable `node:22-alpine` container that the script provisions. This is the authoritative entry point — there is no host-side setup step.

Scripts registered in `frontend/package.json` for reference:

- `test` — interactive Vitest (invoked inside the container when iterating).
- `test:run` — single-shot CI run that `./run_tests.sh` executes inside the container.

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
- file access requires valid token state plus package- and file-level permission checks
- audit logs are append-only and hash-linked for tamper evidence

## Security Notes

- Authentication is fully local-only with no external identity providers.
- Production-style startup (`./start.sh` / `docker-compose up`) fails fast unless strong runtime secrets are supplied — placeholder values are rejected by backend settings validation.
- Demo credentials above are **only** loaded when `.compose.demo.env` (or equivalent explicit demo env) is used with `ALLOW_INSECURE_DEV_MODE=true`. Never deploy demo mode to any shared or production environment.
- Sensitive profile fields are persisted through PostgreSQL `pgcrypto`-backed encrypted columns.
- Passwords use Argon2id hashing.
- Refresh tokens and download tokens are stored hashed.
- RBAC is enforced in backend APIs and mirrored in frontend navigation and route guards.
- Standardized JSON error envelopes avoid leaking stack traces to clients.

## Database-Side Encryption

- PostgreSQL `pgcrypto` is enabled by migration (`enable_pgcrypto_db_encryption`) and used to encrypt `participant_profiles.encrypted_payload` in-database.
- Profile and profile-version payloads are stored through `PgcryptoEncryptedText` / `PgcryptoEncryptedJSON` columns.
- Runtime controls:
  - `DB_ENCRYPTION_ENABLED=true|false` (default `true`)
  - `DB_ENCRYPTION_KEY=<passphrase>` (recommended)
  - fallback key: `ENCRYPTION_KEY` when `DB_ENCRYPTION_KEY` is unset
- Key management guidance:
  - provision `DB_ENCRYPTION_KEY` via environment variables or secret manager
  - rotate with a controlled migration/re-encryption window
  - never keep production keys in source-controlled `.env` files

## Test Coverage Included

### Backend unit tests
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

### Backend API tests (no-mock, real FastAPI + real PostgreSQL)
- `GET /health` — success, method-not-allowed, request-id propagation
- registration / login / lockout
- refresh flow and revocation after password change
- `POST /api/v1/auth/logout` — success, unauthenticated, malformed bearer, unknown refresh token
- forced password change
- profile CRUD including `POST /api/v1/profiles/me` — success, unauthenticated, non-participant forbidden, invalid payload
- plan CRUD and versions
- declaration lifecycle
- reviewer correction workflow
- delivery download valid vs expired
- acceptance confirmation
- notifications, mute settings, and `GET /api/v1/notifications/mandatory-alerts` — scoped filter, unauthenticated, role-scoped empty result
- import/export
- admin disable/reset
- audit log query

### Frontend unit tests (Vitest + Vue Test Utils + jsdom)
- `src/components/common/StatusBadge.spec.ts` — renders label and selects tag type per status class
- `src/stores/auth.spec.ts` — login/logout/clearSession state transitions with success and failure paths
- `src/router/index.spec.ts` — route metadata and `authNavigationGuard` redirect behavior for unauthenticated, forced-password-change, and role-mismatch cases
- `src/api/client.spec.ts` — bearer header attachment, 401 unauthorized handler wiring, `unwrap`, and `extractApiError` variants
