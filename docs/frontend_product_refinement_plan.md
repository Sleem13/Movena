# Frontend Product Refinement Plan

## Current Position

The React dashboard already provides Home, Analyze, Results, and About/Safety behavior for the squat MVP. It should remain the reference web workflow while the information architecture expands gradually.

## Future Pages

- **Landing:** value proposition, intended use, safety boundaries, and role-specific entry points.
- **Analyze:** exercise selection followed by exercise-specific recording guidance and upload options.
- **Results:** consistent validity/confidence shell with exercise-specific metrics and visuals.
- **Session History:** searchable authorized sessions, processing status, retention, export, and deletion.
- **Exercise Library:** active/planned status, purpose, recording view, instructions, and limitations.
- **Patient Profile:** minimal preferences, consent, accessibility, and assigned programs.
- **Therapist Dashboard:** caseload, review queue, plans, trends, notes, and audit-aware sharing.
- **Settings:** privacy, retention, notifications, permissions, locale, and account controls.
- **About/Safety:** intended use, evidence status, confidence, limitations, stop guidance, and version information.

## Component Direction

Retain the current common UI primitives and AppShell, then add route-based pages, typed API models, exercise metadata cards, session-state components, and a reusable `AnalysisResultShell`. Exercise-specific visualizations should be injected into the shell rather than accumulating squat conditionals across generic components.

## Safe Increment Plan

1. Introduce a router only when deep links/session IDs require it; preserve current navigation tests.
2. Add an Exercise Library page backed by the future catalog, showing squat as active and all others as planned.
3. Add a Session History empty state before persistence, with no fabricated data.
4. Expand About into Product Roadmap and Safety sections.
5. Add authenticated patient and therapist surfaces only after the backend authorization model exists.

## UX Requirements

- Rejected inputs never show a normal score or experimental ML judgment.
- Confidence and limitations appear near results, not only in footnotes.
- Planned exercises cannot invoke analysis.
- Loading distinguishes uploading, queued, processing, report generation, and failure.
- Mobile, keyboard, screen-reader, contrast, and reduced-motion behavior are tested.
- Clinical decisions and treatment changes are always directed to a qualified professional.

No placeholder pages are implemented in this roadmap task; the working squat frontend remains unchanged.
# Therapist Workspace Prototype

Sprint 11 adds dashboard summary cards, recent sessions, issue counts, exercise distribution, placeholder-profile creation/list/detail, progress summaries, and visible privacy warnings using the existing component system. Heavy chart and routing dependencies remain deferred. Accessibility, responsive tables, authenticated deep links, and production empty/error-state research remain future refinement work.

