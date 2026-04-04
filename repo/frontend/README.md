# Frontend Implementation Notes

The frontend is a Vue 3 + Vite + TypeScript SPA with Naive UI. It mirrors backend RBAC and exposes separate participant, reviewer, and administrator workspaces.

## Implemented screens
- auth: login, registration, forced password change, unauthorized, not found
- participant: dashboard, profile, plans, declarations, deliveries, notifications
- reviewer: dashboard, queue, package detail with history, correction tools, and delivery publishing controls
- administrator: dashboard, declarations, users, audit log, import/export jobs, settings

## Key shipped behaviors
- route guards mirror backend roles
- declaration detail shows lifecycle history, correction workflow, and delivery workspace
- reviewer/admin users can publish artifacts, restrict them by role, and generate secure links
- admin import/export view supports job creation, job inspection, and secure artifact downloads instead of raw storage paths

## Running locally
1. Install dependencies from `package.json`.
2. Start the dev server with `npm run dev` from `frontend/`.
3. Build with `npm run build`.

## Current boundaries
- secure links are session-driven UI flows; tokens are displayed when created but are not persisted in the client after refresh
- the SPA assumes the backend is available at `/api/v1`
