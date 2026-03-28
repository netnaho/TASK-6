# API Endpoint Inventory

All endpoints are rooted at `/api/v1` and return a standard envelope:

```json
{
  "success": true,
  "message": "optional human-readable message",
  "data": {},
  "meta": {}
}
```

Errors return:

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "code": "validation_error",
      "field": "password",
      "detail": "Password must include at least 3 character classes."
    }
  ]
}
```

## Auth
- `POST /auth/register` - local participant registration
- `POST /auth/login` - username/password login with optional CAPTCHA verification
- `POST /auth/refresh` - rotate refresh token and issue new access token
- `POST /auth/logout` - revoke refresh token
- `POST /auth/change-password` - authenticated password change with history check
- `POST /auth/complete-forced-password-change` - completes admin-forced reset flow
- `GET /auth/me` - current user/session info
- `GET /auth/captcha/challenge` - local CAPTCHA challenge when enabled

## Users and admin account controls
- `GET /users/me/preferences` - current notification preferences and profile flags
- `PATCH /users/me/preferences` - update mutable preferences
- `GET /admin/users` - paginated user list
- `POST /admin/users` - create reviewer/admin/user accounts
- `PATCH /admin/users/{user_id}` - activate/deactivate/update role metadata
- `POST /admin/users/{user_id}/reset-password` - offline admin reset and force-password-change flag
- `GET /admin/users/{user_id}/password-history` - metadata only, not hashes

## Profiles
- `GET /profiles/me` - current participant profile
- `POST /profiles/me` - create profile
- `PUT /profiles/me` - update profile and create new version
- `GET /profiles/me/history` - paginated version history
- `GET /profiles/me/history/{version_id}` - profile version snapshot and diff summary
- `GET /admin/profiles/{profile_id}` - admin/reviewer view subject to permissions

## Nutrition plans
- `GET /plans` - participant plan list or role-filtered admin/reviewer view
- `POST /plans` - create plan draft with phased goals
- `GET /plans/{plan_id}` - plan detail with current phases
- `PUT /plans/{plan_id}` - update plan and create version
- `GET /plans/{plan_id}/versions` - version history
- `GET /plans/{plan_id}/versions/{version_id}` - version snapshot and what-changed summary
- `POST /plans/{plan_id}/duplicate` - create derived draft from existing version

## Declaration packages
- `GET /declarations` - paginated package list with filters by role, state, deadline, reviewer
- `POST /declarations` - create declaration draft tied to profile/plan versions
- `GET /declarations/{package_id}` - package detail, state timeline, deadline, linked versions, delivery summary
- `PUT /declarations/{package_id}` - update package draft metadata
- `POST /declarations/{package_id}/submit` - transition draft to submitted
- `POST /declarations/{package_id}/withdraw` - participant withdrawal
- `POST /declarations/{package_id}/reopen` - withdrawn back to draft
- `POST /declarations/{package_id}/void` - administrative void
- `GET /declarations/{package_id}/history` - package versions and state history
- `GET /declarations/{package_id}/history/{version_id}` - package snapshot and what-changed summary

## Reviewer queue and corrections
- `GET /reviews/queue` - reviewer queue with visible deadlines and overdue indicators
- `POST /reviews/{package_id}/claim` - reviewer claims package
- `POST /reviews/{package_id}/start` - mark in review
- `POST /reviews/{package_id}/request-correction` - create structured correction request and transition to corrected
- `GET /reviews/{package_id}/corrections` - correction thread/history
- `POST /reviews/{package_id}/corrections/{correction_id}/mention` - notify mentioned users
- `POST /reviews/{package_id}/complete` - close review assignment after acceptance or admin closeout
- `POST /declarations/{package_id}/corrections/{correction_id}/acknowledge` - participant acknowledgement
- `POST /declarations/{package_id}/corrections/{correction_id}/resubmit` - participant resubmission back to submitted

## Deliveries and downloads
- `GET /deliveries/{package_id}` - delivery list and statuses for case
- `POST /deliveries/{package_id}/files` - upload/generate delivery artifact
- `POST /deliveries/{package_id}/bulk-download` - generate bulk bundle and token
- `POST /deliveries/{package_id}/links` - create expiring link for file or bundle
- `GET /downloads/{token}` - validate token, permission, expiry, and stream file
- `POST /deliveries/{package_id}/acceptance` - client acceptance confirmation
- `GET /deliveries/{package_id}/acceptance` - acceptance history

## Notifications
- `GET /notifications` - paginated notifications
- `POST /notifications/{notification_id}/read` - mark read
- `POST /notifications/read-all` - bulk mark read
- `PATCH /notifications/preferences` - mute/unmute non-critical categories
- `GET /notifications/mandatory-alerts` - dedicated compliance alerts view

## Import/export
- `POST /imports` - upload CSV/XLSX with mapping selection
- `GET /imports` - import job list
- `GET /imports/{job_id}` - import job result and errors
- `POST /exports` - export request with masking policy
- `GET /exports` - export job list
- `GET /exports/{job_id}` - export metadata and checksum
- `GET /exports/{job_id}/download-link` - expiring link for export artifact
- `GET /admin/field-mappings` - list mappings
- `POST /admin/field-mappings` - create mapping
- `PUT /admin/field-mappings/{mapping_id}` - update mapping
- `GET /admin/masking-policies` - list masking policies
- `POST /admin/masking-policies` - create policy
- `PUT /admin/masking-policies/{policy_id}` - update policy

## Audit and reporting
- `GET /audit` - paginated audit query by actor, entity, action, date range
- `GET /audit/{audit_id}` - audit detail with tamper-evidence metadata
- `GET /admin/reviewer-workload` - reviewer workload dashboard data
- `GET /admin/settings` - system settings
- `PUT /admin/settings` - update configurable local settings
