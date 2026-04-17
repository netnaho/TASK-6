# Remediation Status Report

Source baseline: `./.tmp/static-audit-report.md`

## Verdict

- Overall remediation status: Partial Pass
- Summary: 6 previously reported issues are statically addressed, 1 is partially addressed, and 1 low-severity documentation issue is addressed.

## Scope

- Review type: static-only verification of previously reported issues
- Not executed: app startup, Docker, tests, migrations, browser flows
- Boundary: this is not a full new audit; it checks the prior report’s tracked issues against the current repository state

## Issue Status

### 1. Documented default startup ships known secrets and demo credentials

- Prior severity: Blocker
- Current status: Addressed
- Evidence: `README.md:5-29`, `README.md:40-45`, `README.md:171-180`, `docker-compose.yml:6-23`, `.compose.example.env:1-12`, `backend/app/core/config.py:106-149`, `init-db.sh:42-94`
- Rationale: The main README now requires a real `.compose.env`, uses `.compose.example.env` only as a template, and documents randomized secure bootstrap via `./init-db.sh`. FastAPI settings now fail startup unless strong secrets are supplied unless `TESTING=true` or `ALLOW_INSECURE_DEV_MODE=true` is explicitly set.

### 2. Password resets and password changes do not revoke existing refresh-token sessions

- Prior severity: High
- Current status: Addressed
- Evidence: `backend/app/services/auth_service.py:136-176`, `backend/app/repositories/user_repository.py:22-24`, `unit_tests/test_token_logic.py:20-42`, `API_tests/test_auth_api.py:90-106`, `API_tests/test_admin_api.py:74-90`
- Rationale: `_set_new_password()` now revokes all active refresh tokens before committing the new password, and both unit and API tests now assert stale refresh tokens are rejected after password changes and admin resets.

### 3. Admin-created accounts bypass the required password-history rule

- Prior severity: High
- Current status: Addressed
- Evidence: `backend/app/services/user_service.py:46-63`, `unit_tests/test_password_history.py:44-63`, `API_tests/test_admin_api.py:93-125`
- Rationale: `UserService.create_user()` now creates an initial `PasswordHistory` record for admin-created users, and new tests cover attempted reuse of the original admin-set password.

### 4. Delivery acceptance is not tied to a verified final artifact or delivered version

- Prior severity: High
- Current status: Addressed
- Evidence: `backend/app/schemas/deliveries.py:14-17`, `backend/app/models/delivery.py:42-50`, `backend/app/api/v1/deliveries.py:38-40`, `backend/app/services/delivery_service.py:298-329`, `API_tests/test_acceptance_api.py:6-87`, `API_tests/test_concurrency.py:29-35`
- Rationale: Acceptance now requires a referenced `delivery_file_id`, validates package ownership, requires a final artifact, requires the file to exist on disk, and rejects version mismatches. The acceptance tests were updated to cover missing artifact, non-final artifact, and mismatched version cases.

### 5. CAPTCHA protection is effectively dormant and the settings UI overstates its control

- Prior severity: Medium
- Current status: Partially Addressed
- Evidence: `backend/app/services/auth_service.py:28-31`, `backend/app/services/auth_service.py:70-79`, `backend/app/api/v1/auth.py:63-67`, `backend/app/jobs/notification_cleanup.py:7-23`, `API_tests/test_auth_api.py:109-124`
- Rationale: The runtime-settings part is improved: auth now reads `enable_local_captcha` from persisted settings, `/auth/captcha/challenge` reflects that setting, and notification cleanup now reads `notifications_retention_days` from runtime settings. However, CAPTCHA activation is still gated only by `user.captcha_required`, and there is still no production code path that sets that flag after failures or risk events.

### 6. Reviewer queue is not restricted to actionable assignments

- Prior severity: Medium
- Current status: Addressed
- Evidence: `backend/app/repositories/declaration_repository.py:27-35`
- Rationale: The reviewer queue query now filters to `queued` and `in_review` assignments only.

### 7. Version-history ordering is assumed rather than guaranteed

- Prior severity: Medium
- Current status: Addressed
- Evidence: `backend/app/models/declaration.py:33-34`, `backend/app/models/profile.py:26-31`, `backend/app/models/plan.py:22-27`, `API_tests/test_profile_api.py:26-35`, `API_tests/test_plan_versions_api.py:27-36`
- Rationale: ORM relationships now define descending ordering for declaration versions, declaration state history, profile versions, and plan versions. Profile and plan API tests now assert newest-first ordering; declaration version ordering is fixed in the relationship and therefore statically consistent with frontend usage.

### 8. README delivery structure is not fully accurate

- Prior severity: Low
- Current status: Addressed
- Evidence: `README.md:78-89`
- Rationale: The incorrect `docs/` entry is no longer present in the documented root structure.

## Residuals Still Relevant From The Prior Report

### CAPTCHA activation logic is still incomplete

- Status: Still Open
- Evidence: `backend/app/models/user.py:31`, `backend/app/services/auth_service.py:76-79`
- Reason: CAPTCHA enforcement still depends on `user.captcha_required`, but no current backend path sets that flag automatically. The current tests still simulate enforcement by mutating the DB directly (`API_tests/test_auth_api.py:39-43`, `API_tests/test_auth_api.py:109-114`).

### Logout still lacks refresh-token ownership verification

- Status: Still Open
- Evidence: `backend/app/api/v1/auth.py:31-38`
- Reason: Logout still revokes any supplied refresh token hash if it exists, without checking that the token belongs to the authenticated user. This was called out in the prior report’s security summary, and it remains unchanged.

## Final Assessment

- The major blocker/high findings from the original report have been materially addressed.
- The main remaining tracked concern is CAPTCHA activation logic, which is only partially fixed.
- A separate residual security weakness from the prior report remains in the logout endpoint’s missing token-ownership check.

## Recommended Next Actions

1. Add a real backend rule for setting `user.captcha_required`, or replace the per-user flag with a clearly defined global/runtime policy.
2. Tighten `/api/v1/auth/logout` so it only revokes refresh tokens owned by the authenticated user.
3. If desired, run a fresh full static audit after those two items to regenerate the baseline report.
