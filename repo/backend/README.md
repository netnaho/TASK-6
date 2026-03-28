# Backend Scaffold Plan

The backend will be implemented as a layered FastAPI service under `backend/app/` with the following boundaries:

- `api/`: route handlers, request parsing, dependency injection, response envelopes
- `core/`: config, constants, logging, exception translation
- `db/`: SQLAlchemy base, sessions, startup seeding
- `models/`: ORM models only
- `schemas/`: Pydantic v2 request and response schemas
- `repositories/`: database access only
- `services/`: business workflows, lifecycle validation, versioning, audit orchestration
- `security/`: password policy, hashing, JWT, encryption, CAPTCHA, RBAC checks
- `jobs/`: APScheduler registration and job implementations
- `storage/`: local disk file manager, PDF generation, checksum utilities
- `utils/`: diffs, pagination, datetime helpers

The backend will own all lifecycle validation, permission checks, audit writes, token handling, file authorization, and scheduled jobs.
