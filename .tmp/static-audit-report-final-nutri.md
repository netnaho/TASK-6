# NutriDeclare Static Audit Report

## 1. Verdict

- Overall conclusion: Fail

## 2. Scope and Static Verification Boundary

- What was reviewed: root documentation and manifests, `docker-compose.yml`, `.compose.defaults.env`, backend FastAPI entry points and route registration, auth/security modules, models/services/repositories for profiles, plans, declarations, deliveries, import/export, audit, scheduled jobs, frontend Vue router/views/components/stores for participant/reviewer/admin flows, and the `unit_tests/` plus `API_tests/` suites.
- What was not reviewed: runtime browser behavior, Docker orchestration behavior on this machine, actual PostgreSQL state after startup, network behavior, and external environment setup beyond static files.
- What was intentionally not executed: project startup, Docker, tests, schedulers, database migrations, browser flows, file downloads, and any external services.
- Which claims require manual verification: actual Compose startup and health checks, browser rendering and interaction quality, Nginx/Vite proxy behavior, real filesystem permissions for stored assets, scheduler timing/execution in a running process, and migration behavior against a clean PostgreSQL instance.

## 3. Repository / Requirement Mapping Summary

- Prompt core business goal: an offline workplace-wellness compliance system with participant/reviewer/admin roles, local username/password auth, guided health profiles, phased nutrition plans with version history and change summaries, declaration lifecycle control, reviewer correction workflows, delivery/download controls with acceptance, notifications, audit trails, import/export, and in-process scheduled jobs.
- Main implementation areas mapped: backend APIs in `backend/app/api/v1/`, business logic in `backend/app/services/`, persistence in `backend/app/models/` and `backend/app/repositories/`, security in `backend/app/security/`, jobs in `backend/app/jobs/`, frontend role workspaces in `frontend/src/views/`, route guards in `frontend/src/router/index.ts`, delivery/history components in `frontend/src/components/`, and static test evidence in `unit_tests/` and `API_tests/`.

## 4. Section-by-section Review

### 1. Hard Gates

#### 1.1 Documentation and static verifiability

Conclusion: Partial Pass

Rationale: Startup, run, and test instructions exist, and backend/frontend entry points are statically discoverable. However, the documented default startup path is insecure by default, and the README directory tree claims a `docs/` directory that is not present in the reviewed root tree. Static verification is therefore possible, but the delivery guidance is not fully trustworthy as an acceptance baseline.

Evidence: `README.md:5-17`, `README.md:65-76`, `README.md:126-142`, `backend/README.md:21-29`, `frontend/README.md:17-24`, `docker-compose.yml:3-58`, `backend/app/main.py:41-76`, `frontend/src/main.ts:10-22`

Manual verification note: Compose startup, health checks, and browser loading were not executed.

#### 1.2 Whether the delivered project materially deviates from the Prompt

Conclusion: Partial Pass

Rationale: The codebase is centered on the requested business domain and includes the major product areas from the prompt. The material deviations are in security/compliance semantics rather than domain scope: insecure documented defaults, ineffective CAPTCHA enablement, password-history gaps for admin-created users, and delivery acceptance that is not bound to a verified final deliverable/version.

Evidence: `README.md:3-4`, `backend/app/api/router.py:3-17`, `backend/app/services/auth_service.py:65-77`, `backend/app/services/delivery_service.py:298-317`, `backend/app/services/user_service.py:45-62`

### 2. Delivery Completeness

#### 2.1 Whether the delivered project fully covers the core requirements explicitly stated in the Prompt

Conclusion: Partial Pass

Rationale: The repository contains implementations for local auth, RBAC, profiles, plans, declarations, corrections, deliveries, notifications, import/export, audit logs, encryption, and scheduled jobs. Core requirement coverage is still incomplete because the password-history rule is not preserved for admin-created users, CAPTCHA is not operationally wired as a real local control, and delivery acceptance can be recorded without a validated final artifact/version.

Evidence: `backend/app/api/v1/auth.py:15-68`, `backend/app/api/v1/profiles.py:13-41`, `backend/app/api/v1/plans.py:13-45`, `backend/app/api/v1/declarations.py:14-87`, `backend/app/api/v1/reviews.py:15-52`, `backend/app/api/v1/deliveries.py:15-48`, `backend/app/api/v1/notifications.py:16-60`, `backend/app/api/v1/imports_exports.py:15-81`, `backend/app/api/v1/audit.py:12-16`, `backend/app/services/user_service.py:45-62`, `backend/app/services/delivery_service.py:298-317`

#### 2.2 Whether the delivered project represents a basic end-to-end deliverable from 0 to 1

Conclusion: Partial Pass

Rationale: This is a full-stack repository with backend, frontend, migrations, compose manifests, documentation, and a substantial static test suite. It does not look like a single-file demo. It still falls short of full delivery acceptance because the documented default deployment posture is insecure and several key business/security rules are only partially enforced.

Evidence: `README.md:33-42`, `README.md:43-87`, `backend/migrations/versions/0001_initial.py:1-1`, `frontend/package.json:6-10`, `API_tests/README.md:1-18`, `unit_tests/README.md:1-17`

### 3. Engineering and Architecture Quality

#### 3.1 Whether the project adopts a reasonable engineering structure and module decomposition

Conclusion: Pass

Rationale: The backend is cleanly decomposed into API, services, repositories, models, security, jobs, and storage layers, and the frontend separates router, stores, APIs, views, layouts, and reusable components. The implementation is not piled into one file.

Evidence: `README.md:45-63`, `backend/app/api/router.py:3-17`, `backend/app/services/auth_service.py:21-169`, `backend/app/services/declaration_service.py:32-341`, `frontend/src/router/index.ts:5-74`, `frontend/src/layouts/AppShell.vue:1-189`

#### 3.2 Whether the project shows maintainability and extensibility rather than a temporary implementation

Conclusion: Partial Pass

Rationale: The repository has a maintainable overall shape, but there are notable design shortcuts that weaken extensibility and correctness: some runtime settings are persisted but never consumed, reviewer queue selection is overly broad, and the frontend assumes implicit ordering for history/version arrays that the backend does not guarantee.

Evidence: `backend/app/services/admin_service.py:47-62`, `backend/app/api/v1/auth.py:64-67`, `backend/app/services/auth_service.py:71-74`, `backend/app/jobs/notification_cleanup.py:7-21`, `backend/app/repositories/declaration_repository.py:26-27`, `backend/app/models/declaration.py:33-36`, `backend/app/models/profile.py:26-30`, `backend/app/models/plan.py:22-26`, `frontend/src/views/participant/PlanEditorView.vue:23-26`, `frontend/src/views/participant/DeclarationDetailView.vue:25-30`, `frontend/src/views/reviewer/ReviewDetailView.vue:64-64`, `frontend/src/views/reviewer/ReviewDetailView.vue:106-106`

### 4. Engineering Details and Professionalism

#### 4.1 Whether engineering details reflect professional software practice

Conclusion: Fail

Rationale: The project includes structured JSON logging, request IDs, exception envelopes, and meaningful validation coverage in several areas. That said, the delivered system still has security-critical flaws: known default secrets/credentials in the documented startup path, stale refresh sessions surviving password changes/resets, incomplete password-history enforcement for admin-created users, and weak delivery-acceptance validation.

Evidence: `backend/app/core/logging.py:8-55`, `backend/app/core/responses.py:4-18`, `backend/app/main.py:54-68`, `README.md:11-15`, `.compose.defaults.env:3-15`, `backend/app/services/auth_service.py:97-118`, `backend/app/services/auth_service.py:131-164`, `backend/app/services/user_service.py:45-62`, `backend/app/services/delivery_service.py:298-317`

#### 4.2 Whether the project is organized like a real product or service rather than a demo

Conclusion: Partial Pass

Rationale: The repository shape, modules, migrations, and tests are product-like. However, the seeded demo accounts and committed development secrets are not just scaffolding; they are part of the README’s default startup path, which leaves the delivered shape closer to a development/demo deployment than a secure compliance deployment.

Evidence: `README.md:5-17`, `README.md:26-31`, `.compose.defaults.env:3-15`, `backend/app/db/seed.py:85-105`

### 5. Prompt Understanding and Requirement Fit

#### 5.1 Whether the project accurately understands and responds to the business goal and constraints

Conclusion: Partial Pass

Rationale: The repository clearly understands the domain and implements most of the requested flows. The main fit problems are with the prompt’s security and compliance constraints: secure offline authentication is weakened by shipped secrets and non-revoked sessions, optional CAPTCHA is not functionally wired, and delivery acceptance is not strongly tied to actual delivered outputs.

Evidence: `README.md:3-4`, `backend/app/services/auth_service.py:65-77`, `backend/app/services/auth_service.py:97-118`, `backend/app/services/delivery_service.py:298-317`, `backend/app/models/delivery.py:22-24`, `backend/app/models/user.py:31-31`

### 6. Aesthetics

#### 6.1 Whether the visual and interaction design fits the scenario and demonstrates reasonable visual quality

Conclusion: Cannot Confirm Statistically

Rationale: There is static evidence of differentiated layouts, responsive breakpoints, role-specific navigation, and dedicated delivery/history screens, but actual rendering correctness, spacing, alignment, hover states, and interaction feedback require browser execution.

Evidence: `frontend/src/styles/main.css:23-105`, `frontend/src/layouts/AppShell.vue:1-189`, `frontend/src/views/participant/DeclarationDetailView.vue:1-160`, `frontend/src/views/reviewer/ReviewDetailView.vue:1-177`, `frontend/src/views/shared/NotificationsView.vue:1-94`

Manual verification note: Browser-based visual review is required.

## 5. Issues / Suggestions (Severity-Rated)

### 1. Documented default startup ships known secrets and demo credentials

Severity: Blocker

Conclusion: Fail

Evidence: `README.md:7-17`, `README.md:26-31`, `.compose.defaults.env:3-15`, `docker-compose.yml:23-32`, `backend/app/core/config.py:8-10`, `backend/app/core/config.py:29-35`, `backend/app/core/config.py:86-105`

Impact: The official startup path can run with committed JWT, refresh-token, CAPTCHA, and encryption secrets plus known demo passwords. In a system positioned as a secure compliance platform, this makes token forgery, account compromise, and profile decryption feasible for anyone with repository access if deployed as documented.

Minimum actionable fix: Make randomized secrets mandatory for first boot, remove committed usable secrets and demo passwords from the default deployment path, and fail startup unless real secrets are supplied for any non-test deployment profile.

### 2. Password resets and password changes do not revoke existing refresh-token sessions

Severity: High

Conclusion: Fail

Evidence: `backend/app/services/auth_service.py:97-118`, `backend/app/services/auth_service.py:128-164`, `backend/app/api/v1/auth.py:48-50`, `backend/app/api/deps.py:19-42`

Impact: A stolen refresh token remains usable after self-service password changes and after administrator resets. Because the forced-password-change endpoint explicitly allows authenticated sessions in the forced-change state, a pre-reset stolen refresh token can still refresh and complete the forced password change, undermining the reset flow’s security purpose.

Minimum actionable fix: Revoke all active refresh tokens for the target user whenever `_set_new_password()` runs, and add explicit tests proving old refresh tokens fail after password change and admin reset.

### 3. Admin-created accounts bypass the required password-history rule

Severity: High

Conclusion: Fail

Evidence: `backend/app/services/user_service.py:45-62`, `backend/app/services/auth_service.py:131-139`, `backend/app/repositories/user_repository.py:15-17`

Impact: The prompt requires new passwords not to match any of the last 5 passwords. Admin-created users never receive an initial `PasswordHistory` entry, so their first password change/reset can reuse the original password without detection.

Minimum actionable fix: Insert a `PasswordHistory` row when administrators create users, and add unit/API tests covering password reuse for admin-created accounts.

### 4. Delivery acceptance is not tied to a verified final artifact or delivered version

Severity: High

Conclusion: Fail

Evidence: `backend/app/models/delivery.py:22-24`, `backend/app/services/delivery_service.py:298-317`, `API_tests/test_acceptance_api.py:24-40`, `API_tests/test_authorization_api.py:402-429`, `API_tests/test_e2e_lifecycle.py:84-105`

Impact: Acceptance does not verify that a final delivery artifact exists, does not validate that `accepted_delivery_version` matches any stored deliverable, and only blocks the special case of a draft package with no files. A participant can therefore record acceptance for a submitted package without any delivery artifact at all, and the test suite currently encodes that weak behavior.

Minimum actionable fix: Require at least one package delivery artifact, require a final artifact or explicit accepted file/version reference, validate that the accepted version maps to stored data, and tighten tests to reject acceptance when those conditions are not met.

### 5. CAPTCHA protection is effectively dormant and the settings UI overstates its control

Severity: Medium

Conclusion: Partial Fail

Evidence: `backend/app/models/user.py:31-31`, `backend/app/services/auth_service.py:56-77`, `backend/app/api/v1/auth.py:64-67`, `backend/app/services/admin_service.py:47-62`, `backend/app/jobs/notification_cleanup.py:7-21`, `frontend/src/views/admin/SettingsView.vue:1-49`, `API_tests/test_auth_api.py:39-43`

Impact: CAPTCHA is only enforced when `user.captcha_required` is already true, but no production path sets that flag. Separately, administrators can save `enable_local_captcha` and `notifications_retention_days` in settings, but auth and notification cleanup still read static config rather than the persisted runtime value. This leaves security/operations controls partially nonfunctional and misleading.

Minimum actionable fix: Define and implement a real CAPTCHA activation rule, or a true global runtime switch, and make auth/job code read persisted runtime settings where the UI claims live control.

### 6. Reviewer queue is not restricted to actionable assignments

Severity: Medium

Conclusion: Partial Fail

Evidence: `backend/app/repositories/declaration_repository.py:26-27`, `frontend/src/views/reviewer/ReviewQueueView.vue:24-29`, `API_tests/test_pagination_api.py:69-79`

Impact: The reviewer queue selects all assignments for the reviewer, not just queued/in-review work. Completed, cancelled, or reassigned items can therefore appear in the working queue, weakening the prompt’s deadline-focused reviewer workflow.

Minimum actionable fix: Filter queue queries to active actionable statuses and add API/UI tests proving completed assignments are excluded.

### 7. Version-history ordering is assumed rather than guaranteed

Severity: Medium

Conclusion: Partial Fail

Evidence: `backend/app/models/declaration.py:33-36`, `backend/app/models/profile.py:26-30`, `backend/app/models/plan.py:22-26`, `frontend/src/views/participant/PlanEditorView.vue:23-26`, `frontend/src/views/participant/DeclarationDetailView.vue:25-30`, `frontend/src/views/reviewer/ReviewDetailView.vue:64-64`, `frontend/src/views/reviewer/ReviewDetailView.vue:106-106`

Impact: The frontend treats `versions[0]` as the latest version for “What changed” and review context, but the backend relationships do not declare ordering. This can produce incorrect timelines or change summaries depending on ORM/database return order.

Minimum actionable fix: Order version and history relationships explicitly, or sort API responses before returning them, and add tests that assert newest-first ordering.

### 8. README delivery structure is not fully accurate

Severity: Low

Conclusion: Partial Fail

Evidence: `README.md:65-76`

Impact: The README’s directory tree claims a `docs/` directory that is not present in the reviewed root tree. This is not a core functional defect, but it reduces documentation reliability for acceptance review.

Minimum actionable fix: Update the README directory tree to match the delivered repository contents.

## 6. Security Review Summary

Authentication entry points: Partial Pass

Evidence and reasoning: Local username/password auth, JWT access tokens, hashed refresh tokens, password policy, lockout, and forced password change are implemented in `backend/app/api/v1/auth.py:15-68`, `backend/app/services/auth_service.py:28-169`, `backend/app/security/passwords.py:10-39`, and `backend/app/security/tokens.py:11-48`. Security is materially weakened by shipped default secrets (`.compose.defaults.env:3-15`) and by refresh tokens surviving password changes/resets (`backend/app/services/auth_service.py:97-118`, `backend/app/services/auth_service.py:131-164`).

Route-level authorization: Pass

Evidence and reasoning: Role checks are consistently applied through `require_roles()` and route dependencies across auth-protected endpoints, including admin, reviewer, participant, import/export, audit, and delivery routes (`backend/app/api/deps.py:45-50`, `backend/app/api/v1/admin.py:16-52`, `backend/app/api/v1/reviews.py:15-52`, `backend/app/api/v1/imports_exports.py:15-81`). Static API tests cover many 401/403 cases (`API_tests/test_auth_api.py:32-36`, `API_tests/test_authorization_api.py:307-320`).

Object-level authorization: Partial Pass

Evidence and reasoning: Package, plan, profile, and delivery object checks exist (`backend/app/security/permissions.py:10-45`) and are exercised by isolation tests (`API_tests/test_data_isolation.py:25-71`). The refresh-token logout path lacks token-ownership verification and revokes any supplied refresh token if its hash exists (`backend/app/api/v1/auth.py:32-39`), so not all security-sensitive objects are bound to the current user.

Function-level authorization: Partial Pass

Evidence and reasoning: Most business actions are guarded at the route layer before invoking services. However, several sensitive services rely on caller discipline rather than always enforcing authorization internally, and the password-reset/session lifecycle flaw shows that function-level security invariants are incomplete (`backend/app/services/auth_service.py:128-164`, `backend/app/services/delivery_service.py:298-317`).

Tenant / user data isolation: Pass

Evidence and reasoning: Participant and reviewer isolation is explicitly implemented through `ensure_package_access`, `ensure_plan_owner`, and `ensure_profile_owner` (`backend/app/security/permissions.py:10-45`), and static API tests cover cross-user and unassigned-reviewer access denial (`API_tests/test_data_isolation.py:25-71`, `API_tests/test_authorization_api.py:398-429`).

Admin / internal / debug protection: Pass

Evidence and reasoning: Admin-only routes for users, settings, audit, archives, imports, and exports all require the administrator role (`backend/app/api/v1/admin.py:16-52`, `backend/app/api/v1/imports_exports.py:15-81`, `backend/app/api/v1/audit.py:12-16`), and participant denial is tested (`API_tests/test_authorization_api.py:307-314`). No obvious unprotected debug endpoints were found beyond `/health`.

## 7. Tests and Logging Review

Unit tests: Partial Pass

Rationale: Unit tests exist for password policy, history, lockout, token logic, lifecycle rules, download expiry, export masking, diff summaries, notification mute rules, and logging redaction. They still miss critical scenarios such as password-history behavior for admin-created users and refresh-token revocation after password changes/resets.

Evidence: `unit_tests/README.md:5-17`, `unit_tests/test_password_policy.py:7-17`, `unit_tests/test_password_history.py:9-39`, `unit_tests/test_lockout.py:8-16`, `unit_tests/test_token_logic.py:6-14`, `unit_tests/test_security_hardening.py:22-49`

API / integration tests: Partial Pass

Rationale: API coverage is broad across auth, lifecycle, corrections, deliveries, notifications, import/export, admin, audit, and isolation. However, the suite misses or encodes key defects: stale refresh tokens after password changes/resets, dormant CAPTCHA triggering, and overly weak delivery-acceptance semantics.

Evidence: `API_tests/README.md:5-18`, `API_tests/test_auth_api.py:8-87`, `API_tests/test_declaration_lifecycle_api.py:12-51`, `API_tests/test_delivery_downloads_api.py:9-98`, `API_tests/test_acceptance_api.py:6-40`, `API_tests/test_e2e_lifecycle.py:8-120`

Logging categories / observability: Pass

Rationale: Logging is structured JSON with request IDs, scheduled jobs log execution details, and major workflows log meaningful context such as package IDs, user IDs, and job stats.

Evidence: `backend/app/core/logging.py:8-55`, `backend/app/main.py:45-51`, `backend/app/services/auth_service.py:47-48`, `backend/app/services/declaration_service.py:136-139`, `backend/app/services/delivery_service.py:178-186`, `backend/app/jobs/scheduler.py:16-38`, `backend/app/jobs/search_index.py:48-62`, `backend/app/jobs/reviewer_stats.py:85-101`

Sensitive-data leakage risk in logs / responses: Partial Pass

Rationale: The log formatter redacts common secret/token/password patterns and the exception handlers return controlled envelopes without stack traces. The main leakage risk is not from runtime logging but from shipped secrets and demo passwords in the repository and README.

Evidence: `backend/app/core/logging.py:21-46`, `backend/app/main.py:54-68`, `unit_tests/test_security_hardening.py:22-42`, `.compose.defaults.env:3-15`, `README.md:11-15`, `README.md:26-31`

## 8. Test Coverage Assessment (Static Audit)

### 8.1 Test Overview

- Unit tests exist under `unit_tests/` and use `pytest` with direct service/model calls (`unit_tests/conftest.py:17-43`).
- API / integration tests exist under `API_tests/` and use `pytest` plus FastAPI `TestClient` (`API_tests/conftest.py:19-56`).
- Test entry points are documented in the root README through `./run_tests.sh` (`README.md:126-142`) and the shell script runs `pytest /workspace/unit_tests /workspace/API_tests -q` (`run_tests.sh:51-80`).
- Important boundary: tests rebuild schema with `Base.metadata.create_all()` rather than running Alembic migrations, so migration behavior is not proven by the automated suite (`API_tests/conftest.py:24-31`, `unit_tests/conftest.py:22-29`).

### 8.2 Coverage Mapping Table

| Requirement / Risk Point | Mapped Test Case(s) | Key Assertion / Fixture / Mock | Coverage Assessment | Gap | Minimum Test Addition |
| --- | --- | --- | --- | --- | --- |
| Password strength and lockout | `unit_tests/test_password_policy.py:7-17`, `unit_tests/test_lockout.py:8-16`, `API_tests/test_auth_api.py:8-17` | Weak passwords raise `ValidationError`; five bad logins set `locked_until`; API returns 401 after lockout | basically covered | Does not connect lockout with CAPTCHA escalation or runtime settings | Add API/unit tests that failed-attempt thresholds activate the intended CAPTCHA behavior |
| Password history rule | `unit_tests/test_password_history.py:9-39` | Reuse of one of the last five passwords raises `ValidationError` for seeded users | insufficient | No coverage for admin-created users, which never receive initial password-history rows | Add unit and API tests for password reuse after `POST /api/v1/admin/users` |
| Refresh rotation and replay rejection | `unit_tests/test_token_logic.py:6-14`, `API_tests/test_concurrency.py:28-33`, `API_tests/test_auth_api.py:19-22` | Refresh returns a new token; replaying the old refresh token returns 401 | insufficient | No coverage for password change/reset revoking old refresh tokens | Add tests proving all existing refresh tokens fail after password change and admin reset |
| Forced password change after admin reset | `API_tests/test_admin_api.py:4-18` | Post-reset login returns `force_password_change: true` | insufficient | Does not verify stale sessions are revoked or that old refresh tokens cannot complete the forced-change flow | Add reset-flow tests with a pre-reset refresh token |
| CAPTCHA local validation | `API_tests/test_auth_api.py:39-75` | Test manually sets `user.captcha_required = True` and checks right/wrong answers | insufficient | Test bypasses the missing production trigger path by editing the DB directly | Add tests around real activation logic and runtime setting control |
| Profile CRUD, version history, and encryption | `API_tests/test_profile_api.py:12-35`, `API_tests/test_profile_encryption_api.py:6-38`, `unit_tests/test_profile_version_encryption.py:8-25` | Profile history endpoints return timestamps; DB stored payload is armored PGP text and not plaintext | sufficient | Runtime migration behavior still unproven | Add one migration-focused integration test if startup/migrations become executable |
| Plan CRUD and version history | `API_tests/test_plan_versions_api.py:12-36`, `unit_tests/test_version_diff_summaries.py:4-8` | Multiple versions exist and have timestamps; diff utility tracks changed fields | basically covered | No assertion that newest-first ordering is guaranteed in API/UI | Add tests asserting ordered version/history responses |
| Declaration lifecycle and correction workflow | `unit_tests/test_lifecycle_transitions.py:11-21`, `API_tests/test_declaration_lifecycle_api.py:12-51`, `API_tests/test_reviewer_corrections_api.py:4-18`, `API_tests/test_e2e_lifecycle.py:42-82` | Legal transitions succeed, illegal ones conflict, correction acknowledge/resubmit flow works | basically covered | No direct test of every illegal transition path at API level | Add targeted API cases for illegal state transitions such as voided to corrected |
| Delivery downloads, permissions, and expiry | `unit_tests/test_download_expiry.py:13-24`, `API_tests/test_delivery_downloads_api.py:9-98` | Expired token rejected; file-level role restrictions enforced; bulk zip download works statically | basically covered | No test for token ownership in logout-like security-sensitive object flows | Add negative cases for cross-user token misuse outside download flow |
| Acceptance confirmation semantics | `API_tests/test_acceptance_api.py:6-40`, `API_tests/test_authorization_api.py:402-429`, `API_tests/test_concurrency.py:19-25`, `API_tests/test_e2e_lifecycle.py:100-105` | Participant owner can accept; duplicates are tolerated/conflicted; draft-with-no-file returns 409 | insufficient | Tests encode the weak behavior and do not require a final artifact or version/file binding | Replace acceptance tests with final-artifact/version validation expectations |
| Notifications and mute protections | `unit_tests/test_notification_mute_rules.py:6-17`, `API_tests/test_notifications_api.py:4-114` | Mandatory alerts stay unmuted; preferences update; mentions and deadline warnings are created | basically covered | No runtime test that saved notification retention setting affects cleanup | Add job-level tests for persisted retention settings if kept as runtime controls |
| Import/export mapping and masking | `unit_tests/test_export_masking.py:5-26`, `API_tests/test_import_export_api.py:6-55` | Explicit masking policy masks fields; mapping transforms import/export keys; secure artifact downloads work | insufficient | No test proves default masking-policy behavior or protects profile exports from accidental unmasked output | Add tests for default-policy application and profile-sensitive-field masking |
| Route authorization and cross-user isolation | `API_tests/test_auth_api.py:32-36`, `API_tests/test_authorization_api.py:307-320`, `API_tests/test_data_isolation.py:25-71`, `unit_tests/test_permission_checks.py:11-30` | 401 on invalid tokens; 403 on admin-only endpoints; outsider participant/reviewer access denied | basically covered | No coverage for refresh-token ownership on logout | Add negative tests for cross-user refresh-token revocation attempts |
| Audit immutability | `API_tests/test_audit_api.py:15-39` | Direct UPDATE/DELETE on `audit_logs` raises; `archived_at` update is allowed | sufficient | Archiving job correctness still unexecuted | Add job-level archive tests if runtime execution becomes allowed |

### 8.3 Security Coverage Audit

Authentication: insufficient

Reasoning: Login, lockout, refresh rotation, malformed token rejection, and forced-password-change basics are covered (`API_tests/test_auth_api.py:8-87`, `unit_tests/test_token_logic.py:6-14`). Severe defects could still remain undetected because no test covers session invalidation after password change/reset, and CAPTCHA activation is only tested through a manual DB toggle.

Route authorization: basically covered

Reasoning: The API suite contains many 401/403 cases for participant/reviewer/admin boundaries and invalid bearer tokens (`API_tests/test_auth_api.py:32-36`, `API_tests/test_authorization_api.py:307-320`). Route-level RBAC failures are unlikely to go unnoticed.

Object-level authorization: insufficient

Reasoning: Cross-user declaration/plan/profile/delivery access is well covered (`API_tests/test_data_isolation.py:25-71`, `unit_tests/test_permission_checks.py:11-30`), but refresh-token object ownership on logout is untested and the acceptance tests do not verify that acceptance is tied to the correct deliverable object.

Tenant / data isolation: basically covered

Reasoning: Participant-to-participant and unassigned-reviewer isolation receive direct test coverage (`API_tests/test_data_isolation.py:25-71`). A severe isolation regression in those core resources would likely be caught. Export masking/isolation for sensitive fields remains under-tested.

Admin / internal protection: basically covered

Reasoning: Admin-only surfaces are tested for participant denial (`API_tests/test_authorization_api.py:307-314`). The main remaining risk is not missing admin route guards, but insecure documented defaults and stale-session behavior after admin reset.

### 8.4 Final Coverage Judgment

Fail

The static suite covers many happy paths and a useful subset of 401/403/404/422/conflict cases, especially around core CRUD, lifecycle, downloads, notifications, and audit immutability. The overall coverage still fails acceptance as a safety net because multiple severe defects could ship while tests remain green: default insecure startup posture is not challenged, stale refresh tokens after password change/reset are untested, admin-created password-history gaps are untested, CAPTCHA activation is only simulated by direct DB mutation, and acceptance tests currently encode the wrong business rule.

## 9. Final Notes

- This audit was static-only and intentionally avoided project startup, Docker, tests, or runtime inference.
- The repository shows substantial product work and broad test intent, but the blocker/high findings are material enough to prevent delivery acceptance.
- The most urgent fixes are the insecure default deployment path, refresh-token revocation on password events, admin-created password-history initialization, and delivery-acceptance validation.
