# API Functional Test Plan

API tests will validate the complete FastAPI workflow surface using seeded demo data and an isolated PostgreSQL test database.

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
