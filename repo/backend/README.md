# Backend Implementation Notes

The backend is a FastAPI service under `backend/app/` that ships the offline compliance workflow used by the frontend SPA.

## Implemented areas
- local authentication, refresh rotation, lockout, CAPTCHA, and forced password change
- participant profile and nutrition plan versioning
- declaration lifecycle transitions, reviewer assignment, correction workflow, and audit logging
- delivery artifact upload, secure-link generation, file-level role restrictions, bulk package download, and acceptance recording
- admin import/export jobs with masking policies, mapping tools, job detail, and secure artifact download links
- admin user management, runtime settings, audit listing, notifications, and scheduled jobs

## Layout
- `app/api/`: HTTP routes under `/api/v1`
- `app/services/`: lifecycle, delivery, import/export, auth, and admin workflows
- `app/repositories/`: query helpers used by services
- `app/models/`: SQLAlchemy models for users, declarations, deliveries, jobs, and audit records
- `app/security/`: RBAC, tokens, password rules, encryption, CAPTCHA
- `app/storage/`: local file persistence and PDF generation helpers

## Running locally
1. Install dependencies from `requirements.txt`.
2. Provide PostgreSQL settings and encryption keys through environment variables.
3. Run `uvicorn app.main:app --reload` from `backend/`.

## Current boundaries
- storage is local-disk backed; secure links are enforced through hashed download tokens plus file/package authorization
- import/export supports the delivered declaration export scope and admin-uploaded import files
- no external identity provider, object storage, or background queue is included in this implementation
