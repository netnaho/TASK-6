# Frontend Routes And Pages By Role

## Shared routes
- `/login` - local login with optional CAPTCHA panel and account lockout messaging
- `/register` - participant registration
- `/force-password-change` - required after admin reset
- `/unauthorized` - RBAC denial page
- `/notifications` - cross-role notification center
- `/profile/history/:versionId` - profile version view when permitted
- `/plans/:planId/versions/:versionId` - plan version viewer
- `/declarations/:packageId/history/:versionId` - package version viewer

## Participant routes
- `/app/participant/dashboard` - status overview, active plan, pending corrections, upcoming deadlines, mandatory alerts
- `/app/participant/profile` - guided health profile wizard with encrypted field indicators and version timeline
- `/app/participant/plans` - plan list
- `/app/participant/plans/new` - phased goal planner builder
- `/app/participant/plans/:planId` - plan detail and phase timeline
- `/app/participant/declarations` - package list with state filters
- `/app/participant/declarations/new` - draft package creation
- `/app/participant/declarations/:packageId` - package detail, lifecycle timeline, delivery status, review due date
- `/app/participant/declarations/:packageId/corrections/:correctionId` - structured correction response workspace
- `/app/participant/deliveries` - all accessible delivery artifacts and acceptance tasks
- `/app/participant/settings` - password change and notification preferences

## Reviewer routes
- `/app/reviewer/dashboard` - queue summary, overdue review cards, workload stats
- `/app/reviewer/queue` - sortable queue table with due-by timestamps and state filters
- `/app/reviewer/packages/:packageId` - review workspace with package details, history, timeline, versions, and delivery artifacts
- `/app/reviewer/packages/:packageId/corrections/new` - structured correction form
- `/app/reviewer/packages/:packageId/history` - version and state history viewer
- `/app/reviewer/settings` - password change and notification preferences

## Administrator routes
- `/app/admin/dashboard` - compliance overview, queue metrics, recent critical audits, job health
- `/app/admin/users` - user directory and account controls
- `/app/admin/users/:userId` - user detail, status, reset action, history summary
- `/app/admin/packages` - all package oversight view
- `/app/admin/packages/:packageId` - administrative package workspace with lifecycle controls
- `/app/admin/imports` - import jobs, mapping selection, result review
- `/app/admin/exports` - export jobs, masking policies, checksum view
- `/app/admin/field-mappings` - mapping management
- `/app/admin/masking-policies` - masking rule management
- `/app/admin/audit` - immutable audit query page
- `/app/admin/settings` - local config such as CAPTCHA toggle, link expiry, retention
- `/app/admin/jobs` - scheduler health and recent runs

## UI composition rules
- one responsive shell with role-aware navigation, pinned alerts, and breadcrumb trail
- dashboard cards vary by role and never expose unauthorized actions
- history pages use side-by-side or stacked diff views depending on breakpoint
- lifecycle badges, due-date chips, and expired-link banners are shared reusable components
