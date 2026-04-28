# Implementation Plan: ACA Scaling Dashboard v2 — Enhanced Monitoring & Navigation

**Branch**: `006-scaling-enhancements` | **Date**: 2026-04-28 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/006-scaling-enhancements/spec.md`  
**Depends On**: `005-aca-scaling-dashboard` (v1) — all v1 features are foundation for v2

## Summary

Enhance the v1 ACA Scaling Dashboard with:
1. **Continuous background polling** at a separate, slower interval (`BACKGROUND_POLLING_INTERVAL_MS`) that runs throughout the entire session, not just during active scaling events, reducing backend load during idle periods
2. **Placeholder-driven initial load** where the page renders immediately with skeleton/placeholder content, then API calls populate real metrics without page jank
3. **Form restoration** so the send button reappears after a scaling event completes, allowing users to run multiple experiments on the same page
4. **Live queue depth updates** in the metric panel during polling (already implemented in v1; v2 documents and may refine this)
5. **Navigation restructure** introducing a top-level "Demo" section grouping Cricket Data and Scaling Dashboard as submenus (impacts site IA)
6. **Eager chart polling** starting immediately on form submission without waiting for 202 response confirmation (server-side or parallel client-side mechanism)

All changes preserve the existing Flask + Jinja + vanilla JS + stdlib architecture. No new dependencies. Polling interval configuration extends v1's existing pattern. Navigation structure is a site-wide IA improvement affecting multiple templates.

## Technical Context

**Language/Version**: Python 3.13, Jinja2 templates, vanilla JavaScript  
**Primary Dependencies**: Flask (existing), `urllib` stdlib for ACA API calls, pytest (existing), python-dotenv (existing)  
**Storage**: N/A — background polling state and chart readings remain in-session memory  
**Testing**: pytest route tests (`tests/test_routes.py`) extended for new features; integration with existing v1 tests  
**Target Platform**: Server-rendered web app for modern desktop/mobile browsers  
**Project Type**: server-rendered web-service  
**Performance Goals**: Initial page load fast with placeholders; background polling keeps metrics fresh without excessive backend load (default 30s interval); chart polling eager start ensures data fidelity  
**Constraints**: No client-side framework; follow existing IIFE + data attribute JS pattern; preserve v1 route behavior; navigation changes are site-wide IA (affects base.html, possibly content.py); no new secrets in source  
**Scale/Scope**: Modifications to v1 `app.py`, `templates/scaling.html`, `static/js/scaling.js`, `content.py` (nav), `static/css/site.css` (may add form-restore styles); base.html navigation restructure; new environment variable `BACKGROUND_POLLING_INTERVAL_MS`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: /scaling page continues to render server-side with initial metrics on first response (Principle I, unchanged from v1).
- PASS: Background polling and placeholder UX are progressive enhancements; core metric display works with JavaScript disabled (Principle III).
- PASS: Navigation changes (Demo section) are site-wide IA, not technology-specific; implemented in Jinja templates and vanilla CSS/JS (Principle III).
- PASS: Responsive behavior verified at 375px (mobile) and 1280px (desktop) for placeholders, form restoration, and nav submenus (Principle II).
- PASS: Polling errors remain non-disruptive; background polling failures do not interrupt active monitoring or user interaction (Principle V, FR-001).
- PASS: All configurable intervals are environment variables; navigation structure is authored in templates; no sensitive data in source (Principle V).

Post-design re-check:

- PASS: API client (`aca_scaling_api.py`) is unchanged; route orchestration in `app.py` handles new polling logic; no business logic in templates or JS.
- PASS: Navigation structure change is centralized in base.html template and content.py; submenus are Jinja-rendered, not dynamic JS.

## Project Structure

### Documentation (this feature)

```text
specs/006-scaling-enhancements/
├── checklists/
│   └── requirements.md
├── contracts/
│   └── (optional: new or updated if nav contracts needed)
├── plan.md                  ← this file
├── spec.md
├── research.md              ← Phase 0 output (if needed)
├── data-model.md            ← Phase 1 output (polling config, nav structure)
├── quickstart.md            ← Phase 1 output (v2 test flows)
└── tasks.md                 ← Phase 2, created by /speckit-tasks
```

### Source Code (repository root) — Changes to v1

```text
app.py
├── /scaling route          ← MODIFIED: placeholder rendering + background polling config
├── /scaling/api/status     ← unchanged from v1
└── /scaling/api/send       ← unchanged from v1

content.py
├── Navigation structure    ← MODIFIED: add "Demo" top-level section with submenus
└── Scaling page content    ← unchanged from v1

templates/
├── base.html               ← MODIFIED: navigation restructure (Demo submenu on desktop + mobile)
└── scaling.html            ← MODIFIED: placeholder markup + form restoration logic + eager polling

static/
├── css/site.css            ← MODIFIED: add placeholder styles, form-restore styles, nav submenu styles
└── js/scaling.js           ← MODIFIED: add background polling loop, placeholder handling, eager polling, form restoration

tests/
├── test_routes.py          ← MODIFIED: add tests for placeholder states, form restoration, background polling
└── test_aca_scaling_api.py ← unchanged from v1
```

**Structure Decision**: All v2 changes are layered on top of v1. No rewrites. API module remains unchanged. Routes remain unchanged in signature. New behavior is added as middleware-like enhancements (e.g., placeholders rendered server-side before metrics fetch; background polling loop runs alongside active monitoring).

## Implementation Phases

### Phase 0: Research and Decision Alignment

- Confirm placeholder design approach: server-rendered skeleton vs. hardcoded placeholder values in data attributes vs. CSS-only placeholders.
- Confirm background polling should use a separate environment variable (`BACKGROUND_POLLING_INTERVAL_MS`, default ~5 seconds).
- Confirm eager chart polling design: server-side polling thread/task vs. client-side parallel fetch after 202.
- Confirm navigation changes (Demo section) scope: Does this affect other pages? Are Cricket Data and Scaling the only demos? Any impact on breadcrumbs or mobile drawer?

### Phase 1: Design Artifacts

- **Data Model**: Background polling configuration (interval, error handling); placeholder state machine; form restoration state; eager polling lifecycle.
- **Contracts**: Updated `/scaling` route (now with placeholder + eager polling semantics); unchanged `/scaling/api/status` and `/scaling/api/send`.
- **Navigation Architecture**: Demo section structure in base.html; content.py mapping for nav hierarchy; mobile submenu interaction pattern.
- **Quickstart**: Verification flows for background polling (metrics update over 60s without interaction), placeholder appearance and replacement, form restoration after completion, eager polling (chart starts immediately), nav Demo section access.

### Phase 2: Incremental Delivery

- **T001–T004**: Background polling loop (separate interval config, error handling, state machine)
- **T005–T007**: Placeholder UX (server rendering, replacement without jank, styling)
- **T008–T009**: Form restoration (button reappearance after completion, state reset)
- **T010–T012**: Navigation redesign (base.html restructure, content.py nav tree, CSS/JS for submenus)
- **T013–T015**: Eager chart polling (immediate data collection on submit)
- **T016–T019**: Tests and validation

## Discrete Agent Tasks

Each task is independently implementable with a clear scope and completion signal.

### Background Polling & Config (T001–T004)

**T001** — Add background polling environment variable and pass to template  
Scope: `app.py` /scaling route  
Deliverable: Read `BACKGROUND_POLLING_INTERVAL_MS` from environment (default 30000); pass to template context as `background_polling_interval_ms`; no JS changes yet.

**T002** — Add background polling loop to scaling.js  
Scope: `static/js/scaling.js`  
Deliverable: Create `startBackgroundPolling()` function that calls `GET /scaling/api/status` at `background_polling_interval_ms` and updates metric panels (reuse `updateReplicaCount()` and `updateQueueDepth()`); start on page load before any message submission; do not interrupt during active monitoring, only resume after monitoring ends.

**T003** — Handle background polling errors without disrupting active monitoring  
Scope: `static/js/scaling.js`  
Deliverable: Background polling catch block logs errors silently; does not stop active polling or show error to user; resumes background polling after active monitoring completes.

**T004** — Test background polling behavior  
Scope: `tests/test_routes.py`  
Deliverable: Add tests confirming `/scaling/api/status` is called correctly; background polling config is passed to template; verify no new regressions in v1 polling behavior during active monitoring.

### Placeholder UX (T005–T007)

**T005** — Create placeholder markup and server-side rendering  
Scope: `templates/scaling.html`  
Deliverable: Add placeholder markup for queue-depth and replica-count metric panels (e.g., skeleton or gray placeholder). Render placeholders immediately; after page renders, JavaScript or HTMX-like mechanic replaces them with real metrics. Ensure placeholder is visually distinct from real data.

**T006** — Replace placeholders with real metrics after API call  
Scope: `app.py` /scaling route + `templates/scaling.html`  
Deliverable: Initial page load renders with placeholders; `/scaling` route makes API call to fetch metrics; JavaScript (or template script) receives real values and replaces placeholders in-place without page reload. Ensure no visible jank or flash.

**T007** — Style placeholders and responsive layout  
Scope: `static/css/site.css`  
Deliverable: Add CSS for placeholder styling (e.g., gray background, shorter text, opacity); ensure placeholder and final metric panels have same height to prevent layout shift; verify responsive at 375px and 1280px.

### Form Restoration (T008–T009)

**T008** — Add form restoration logic to scaling.js  
Scope: `static/js/scaling.js`  
Deliverable: After monitoring stops (queue empty or timeout), transition form from hidden to visible; reset form inputs to empty state; reset button to enabled state. Preserve all other page state (chart, metric panels, status message).

**T009** — Test form restoration and re-submission  
Scope: `tests/test_routes.py`  
Deliverable: Add test confirming form reappears after scaling event; add test confirming second message submission works on same page; verify form state is properly reset.

### Navigation Redesign (T010–T012)

**T010** — Restructure navigation in base.html with Demo section  
Scope: `templates/base.html`  
Deliverable: Add top-level "Demos" nav item with "Cricket Data" and "Scaling" as submenus. On desktop: horizontal dropdown on hover/focus. On mobile (375px): expand/collapse with tap. Ensure all nav items remain accessible.

**T011** — Update content.py navigation structure  
Scope: `content.py`  
Deliverable: Modify navigation hierarchy to include "Demos" section with nested items. Ensure "Cricket Data" and "Scaling" pages set correct `page_name` or `active_nav` state so the appropriate link is marked active when viewing that page.

**T012** — Style Demo submenu and responsive behavior  
Scope: `static/css/site.css` + `static/js/site_nav.js` (if exists)  
Deliverable: Add styles for submenu appearance (dropdown on desktop, drawer/collapse on mobile). Add minimal JS to toggle mobile submenu. Ensure submenu opens/closes within 300ms; no layout shift; fully usable on both 375px and 1280px.

### Eager Chart Polling (T013–T015)

**T013** — Start chart polling immediately on form submission  
Scope: `static/js/scaling.js`  
Deliverable: On form submit (before 202 response), call `startChartPolling()` function that begins polling `/scaling/api/status` and accumulating readings immediately. Do not wait for 202. Parallel to form submission request.

**T014** — Ensure chart data starts at elapsed_ms ≈ 0  
Scope: `static/js/scaling.js`  
Deliverable: First chart reading has `elapsed_ms` approximately 0 (within 500ms of submission). Chart renders correctly with single data point; no gaps in data when 202 arrives late.

**T015** — Test eager polling behavior  
Scope: `tests/test_routes.py`  
Deliverable: Add test confirming chart receives first reading immediately after submission; verify no data loss if 202 response is delayed.

### Documentation & Validation (T016–T019)

**T016** — Write research.md (if needed)  
Scope: `specs/006-scaling-enhancements/research.md`  
Deliverable: Document decisions on placeholder design, polling interval defaults, eager polling implementation, nav structure impact.

**T017** — Write data-model.md  
Scope: `specs/006-scaling-enhancements/data-model.md`  
Deliverable: Document polling configuration entity, placeholder states, form restoration state machine, navigation hierarchy.

**T018** — Write quickstart.md  
Scope: `specs/006-scaling-enhancements/quickstart.md`  
Deliverable: Test scenarios: background polling updates metrics every 30s without submission; placeholder appears and is replaced with real metrics; form reappears and allows re-submission; chart starts immediately on submission; nav Demo section is accessible on desktop and mobile.

**T019** — Run full test suite and verify against spec  
Scope: `pytest` suite  
Deliverable: All existing v1 tests pass; all new tests pass; no regressions; manual verification of quickstart scenarios; responsive layout checked at 375px and 1280px.

## Implementation Notes

- **Background polling**: Reuse existing `/scaling/api/status` endpoint (unchanged from v1). Add new config variable and JavaScript loop. Keep background polling separate from active monitoring to allow different intervals.
- **Placeholders**: Consider CSS approach (gray divs with fixed height) or skeleton screens. No new template variables needed if using CSS-only approach.
- **Form restoration**: Reuse existing form element and buttons; just toggle visibility and reset input values. No new API endpoint.
- **Navigation**: This is a site-wide change affecting base.html and potentially other templates. Coordinate with overall site IA. Consider impact on other pages (do they appear in Demo section? Are there other top-level sections?).
- **Eager polling**: Decide server-side vs. client-side. Server-side: background job or timer on /scaling/api/send. Client-side: JavaScript starts polling loop immediately on submit, parallel to fetch. Client-side is simpler and fits v1 architecture.
- **Testing**: Extend existing pytest patterns from v1. Mock `/scaling/api/status` responses; test polling frequency and state transitions.

## Success Criteria

- All v1 functionality remains intact and tested.
- Background polling runs at configurable interval (default 30s) throughout entire session.
- Placeholders render immediately; replaced by real metrics within 500ms without jank.
- Form reappears within 500ms of scaling event completion; allows re-submission on same page.
- Chart receives first reading within 500ms of form submission; no data loss.
- Navigation Demo section is fully navigable on 375px mobile and 1280px desktop.
- All tests pass; no regressions.

## Dependencies & Blockers

- **No new dependencies**. All features implementable with existing Flask, Jinja, vanilla JS, pytest.
- **Navigation changes are site-wide IA**: Confirm scope with stakeholder before Phase 1 design.
- **Eager polling server-side implementation** (if chosen): Depends on ACA API's ability to start collecting metrics server-side on message submission acceptance.

## Rollback & Iteration Strategy

- Background polling: Can be disabled by setting `BACKGROUND_POLLING_INTERVAL_MS` to a very large value or conditionally in code. No route changes required.
- Placeholders: Can be removed by deleting placeholder markup; renders will be immediate with real metrics.
- Form restoration: Can be disabled by keeping form hidden after completion; restores v1 behavior (no re-submission without refresh).
- Navigation: Can be reverted to flat nav by removing Demo section from base.html.
- Eager polling: Can be disabled by removing eager polling call; chart will start after 202 (v1 behavior).

Each feature can be toggled or reverted independently.
