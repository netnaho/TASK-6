# NutriDeclare Offline Compliance System - API Specification

## Overview
The NutriDeclare API is a locally-hosted RESTful API built on FastAPI. It serving the Vue 3 frontend in an offline, internet-free environment.
All endpoints (except login/registration flows) require authentication via Bearer JWT Access Tokens.

**Base URL**: `http://localhost:8000/api/v1`

---

## 1. Authentication & Identity (`/auth`)
*Offline, local token generation and user identity.*

- `POST /auth/register` - Register a new offline participant account.
- `POST /auth/login` - Authenticate local username/password. Returns JWT access token (30m) and refresh token (7d).
- `POST /auth/refresh` - Refresh an expired access token using a valid refresh token.
- `POST /auth/logout` - Invalidate the current session and refresh tokens.
- `POST /auth/change-password` - Update password (enforces 12 chars, complexity, and history uniqueness).
- `POST /auth/complete-forced-password-change` - Fulfill admin-forced offline password reset.
- `GET  /auth/me` - Retrieve current session identity and role.
- `GET  /auth/captcha/challenge` - Generate an offline CAPTCHA for mitigating local brute-force scripts.

## 2. Profiles (`/profiles`)
*Participant health profile management (encrypted at rest).*

- `GET  /profiles/me` - Retrieve the current participant's active health profile.
- `POST /profiles/me` - Create the initial health profile.
- `PUT  /profiles/me` - Update profile data.
- `GET  /profiles/me/history` - List all historical snapshots of the health profile.
- `GET  /profiles/me/history/{version_id}` - Retrieve a specific historical snapshot.

## 3. Nutrition Plans (`/plans`)
*Phased nutrition goal strategies.*

- `GET  /plans` - List plans for the authenticated user.
- `POST /plans` - Create a new phased nutrition plan.
- `GET  /plans/{plan_id}` - Retrieve active plan details.
- `PUT  /plans/{plan_id}` - Modify existing plan parameters (creates new versions if submitted).
- `GET  /plans/{plan_id}/versions` - List historical versions.
- `GET  /plans/versions/{version_id}` - Fetch a specific plan version.

## 4. Declaration Lifecycle (`/declarations`)
*Core compliance records. State transitions are strictly enforced algorithmically.*

- `GET  /declarations` - List declaration packages.
- `POST /declarations` - Initialize a new declaration in `Draft` state.
- `GET  /declarations/{package_id}` - Get full package details including status overlays.
- `POST /declarations/{package_id}/submit` - Transition state: `Draft`/`Corrected` -> `Submitted`. Freezes current profile/plan states.
- `POST /declarations/{package_id}/withdraw` - Transition state: `Submitted` -> `Withdrawn`.
- `POST /declarations/{package_id}/reopen` - Transition state: `Withdrawn` -> `Draft`.
- `POST /declarations/{package_id}/void` - Terminate package. Irreversible.
- `GET  /declarations/{package_id}/history` - Detailed timeline of state changes and what changed.
- `GET  /declarations/{package_id}/corrections` - Fetch reviewer correction requests.
- `POST /declarations/{package_id}/corrections/{correction_id}/acknowledge` - Participant acknowledges feedback.
- `POST /declarations/{package_id}/corrections/{correction_id}/resubmit` - Respond to feedback and return to `Submitted`.

## 5. Reviewer Operations (`/reviews`)
*Restricted to the Reviewer and Administrator roles.*

- `GET  /reviews/queue` - Poll the centralized review queue for `Submitted` packages indicating SLA deadlines.
- `POST /reviews/{package_id}/request-correction` - Shift package to `Corrected` state, appending structured feedback.
- `GET  /reviews/{package_id}/corrections` - View correction thread.
- `POST /reviews/{package_id}/complete` - Approve package, initiating delivery phase.

## 6. Deliveries & Downloads (`/deliveries`, `/downloads`)
*Asset distribution with RBAC and explicit expiration rules.*

- `GET  /deliveries/{package_id}` - List assets tied to an approved package.
- `POST /deliveries/{package_id}/accept` - Participant explicitly approves delivery terms (Compliance Confirmation).
- `POST /deliveries/{package_id}/generate-token` - Generate an expiring, permission-gated access token for assets.
- `GET  /downloads/{token}` - Retrieve specific encrypted asset payload directly to local disk.

## 7. Notifications (`/notifications`)
*Local polling-based app alerts.*

- `GET  /notifications` - List user alerts.
- `POST /notifications/{notification_id}/read` - Mark specific alert as read.
- `POST /notifications/read-all` - Bulk clear unread status.
- `GET  /notifications/preferences` - Retrieve current audio/visual mute settings.
- `PATCH /notifications/preferences` - Toggle specific non-critical alert classes.
- `GET  /notifications/mandatory-alerts` - Fetch compliance alerts (cannot be muted).

## 8. Administration & Audit (`/admin`, `/audit`, `/imports-exports`)
*Restricted to Administrator workflows.*

- `GET  /admin/users` - Directory of local accounts.
- `POST /admin/users` - Pre-provision accounts.
- `PATCH /admin/users/{user_id}` - Disable/Lock accounts.
- `POST /admin/users/{user_id}/reset-password` - Force an offline password reset on next login.
- `GET  /admin/settings` - Toggle runtime controls (e.g., SLA windows, DB encryption fallbacks).
- `GET  /audit` - Search against the immutable, hash-linked application audit records.
- `GET  /admin/audit-archives` - Manage 7-year retention archives.
- `GET  /imports-exports/schema` - Read admin-defined schema mapping.
- `POST /imports-exports/export` - Trigger a local file generation masking data via policy policies. Includes checksum hash.
