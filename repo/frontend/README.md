# Frontend Scaffold Plan

The frontend will be implemented as a Vue 3 + Vite + TypeScript SPA using Naive UI consistently across all screens.

Planned frontend structure:
- `src/router/`: role-aware route records and guards
- `src/stores/`: Pinia stores for auth, notifications, app shell, and preferences
- `src/api/`: Axios clients grouped by backend domain
- `src/layouts/`: authenticated and unauthenticated shells
- `src/components/`: reusable enterprise UI modules for cards, forms, tables, timelines, histories, badges, and download states
- `src/views/`: role-specific pages for participant, reviewer, and administrator
- `src/composables/`: reusable view logic and breakpoint helpers
- `src/types/`: shared DTO typing aligned with backend schemas
- `src/styles/`: design tokens, theme overrides, layout primitives

The UI target is a premium internal SaaS experience with responsive dashboards, robust loading/error states, and no dead-end flows.
