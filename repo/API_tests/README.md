# API Functional Test Plan

API tests validate the complete FastAPI workflow surface using an isolated PostgreSQL test database plus committed test-only credentials from `.compose.test.env`.

Mandatory suites:
- registration, login, and lockout
- refresh flow
- forced password change
- profile CRUD
- goal plan CRUD and versions
- declaration lifecycle endpoints
- reviewer correction flow
- delivery and download valid versus expired
- acceptance confirmation
- notifications and mute settings
- import and export
- admin disable and reset
- audit log query
