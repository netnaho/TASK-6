# NutriDeclare Offline Compliance System - System Design

## 1. System Overview
The NutriDeclare Offline Compliance System is an offline-first compliance platform designed to manage workplace wellness workflows. It enables organizations to securely maintain employee health profiles, manage phased nutrition planning, and strictly control declaration lifecycles without requiring external network connectivity or cloud services. The system natively supports three primary actors: Participants (employees), Reviewers (wellness coordinators), and Administrators.

## 2. Architectural Principles
- **Offline-First Operability:** No external dependencies, third-party APIs (no email/SMS), or external internet access is required.
- **Local Security Controls:** Exclusively local authentication, RBAC enforcement, and encryption to satisfy strict data privacy policies without relying on IDPs like Okta/Auth0.
- **Performant Micro-Monolith:** The backend operates as a decoupled REST API using FastAPI. It bundles all necessary backend components (background jobs, file storage, endpoints) into a single performant service to prioritize ease of on-premise deployment.

## 3. High-Level Architecture

### 3.1 Frontend (Vue 3 SPA)
- **Tech Stack:** Vue 3 with Vite, TypeScript.
- **State Management:** Pinia isolates reactive store management (auth session, notifications, UI shells).
- **Routing & Guards:** Vue Router implements absolute Role-Based Access Control (RBAC) mirrored from backend APIs to prevent unauthorized rendering.
- **UI Framework:** Naive UI provides robust, accessible interfaces suitable for compliance, including data tables, timeline visualizations, and delivery tracking.
- **Code Organization:**
  - `src/layouts/`: Differentiates authenticated shells from unauthenticated views.
  - `src/views/`: Dedicated workspaces for Participant, Reviewer, and Admin roles.
  - `src/api/`: Modular Axios wrappers ensuring standardized local API interaction.

### 3.2 Backend (FastAPI Service)
- **Tech Stack:** FastAPI using Pydantic v2 for stringent request/response validation.
- **Pattern:** Layered architecture (`api`, `core`, `db`, `models`, `repositories`, `services`, `security`, `jobs`, `storage`).
- **Scheduling:** In-process `APScheduler` manages nocturnal search index rebuilding, workload stat refreshing, and expired token cleanup autonomously.
- **Storage Strategy:** Local file-system volume mounts for document storage (PDFs, exports) coupled with database validation pointers and permission checks on every file download request.

### 3.3 Database & State (PostgreSQL)
- **System of Record:** PostgreSQL handles relational boundaries for accounts, profiles, phase milestones, and immutable audit trails.
- **Migrations:** Alembic is used for structured schema evolution and database startup initialization.
- **Seeding:** The Fast API app automatically bootstraps the database with seed and demo data upon initial startup.

## 4. Security & Compliance Controls

- **Authentication Policies:** 
  - Local Username/Password flow only.
  - Passwords enforce minimum complexity (12 chars, 3 of 4 classes) and maintain a rolling 5-password uniqueness history.
  - Accounts explicitly lock out for 15 minutes following 5 consecutive failed login attempts.
- **Session Management:** Signed JWT access tokens (30 min TTL), paired with hashed Refresh tokens (7 day TTL).
- **Data at Rest (Encryption):** 
  - Application-layer AES-256-GCM symmetric encryption for sensitive fields before transit to DB.
  - Database-native encryption utilizing PostgreSQL `pgcrypto` (`DB_ENCRYPTION_ENABLED`) extending protection to the persistent payload layer.
- **Audit Trails:** Every domain mutation generates an immutable, append-only, temporally-sequenced audit log record. Export packages implement local checksum hashes for tamper-evident verification.

## 5. Domain Lifecycles & State Management

**Declaration State Machine**
Enforced entirely on the server-side, preventing illegal state transitions algorithmically:
1. `Draft`: Active formulation by the Participant.
2. `Submitted`: Locked for participant edits; creates an immutable snapshot version and transitions to Reviewer queues.
3. `Withdrawn`: Participant retracts the submission prior to active review.
4. `Corrected`: Reviewer kicks back the declaration demanding structured revisions.
5. `Voided`: Fully terminated state, irrecoverable to `Corrected` or `Submitted`.

## 6. Notification & Asset Delivery Workflow

- **In-App Messaging:** Real-time UI notifications broadcasting approaching deadlines, profile mentions, and review requests. Users can "mute" non-critical events, but mandatory compliance alerts definitively bypass these preferences.
- **Asset Packages:** Final deliveries compile PDFs, exports, and specific revision notes. Downloads enforce strict temporal expirations (default: 72 hours) and contextual role RBAC. Furthermore, workflows mandate a 'Client Acceptance Status' confirmation directly tied to the participant acknowledging receipt and comprehension of the documentation.
