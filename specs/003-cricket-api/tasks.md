# Tasks: Cricket API Integration

**Input**: Design documents from `/specs/003-cricket-api/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Include route-level tests because the feature adds new server-rendered routes, an upstream integration module, and degraded behavior for backend failures.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently by an AI coding agent.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when the tasks touch different files and have no direct dependency.
- **[Story]**: User story identifier from the spec (`US1`, `US2`, etc.).
- Every task includes exact file paths.

## Phase 1: Setup

**Purpose**: Establish the minimal scaffolding for an upstream-backed matches feature.

- [X] T001 Review `specs/openapi.yaml` and the sample document in `specs/63963.json` to define browse and detail behavior.
- [X] T002 Update `README.md` with environment configuration notes for `MATCHES_API_BASE_URL`.

---

## Phase 2: Foundational

**Purpose**: Build the integration layer and navigation support shared by all stories.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [X] T003 Create `matches_api.py` with browse query parsing, upstream HTTP GET helpers, error mapping, and response normalization.
- [X] T004 [P] Add concise info-summary derivation helpers to `matches_api.py`.
- [X] T005 [P] Update `content.py` navigation data to include the `Matches` top-level nav item.

**Checkpoint**: Routes can now rely on a stable integration layer and shared navigation state.

---

## Phase 3: User Story 1 - Search for Matches (Priority: P1) 🎯 MVP

**Goal**: Deliver a Flask-rendered browse page with all supported backend filters and search results.

**Independent Test**: Open `/matches`, confirm the form renders all required filters, submit at least one filter, and verify server-rendered result cards are shown.

### Tests for User Story 1

- [X] T006 [P] [US1] Extend `tests/test_routes.py` with coverage for `GET /matches` form rendering and browse result display.

### Implementation for User Story 1

- [X] T007 [US1] Add the `/matches` route to `app.py` and connect it to `matches_api.py` browse behavior.
- [X] T008 [US1] Create `templates/matches.html` for the server-rendered browse form, results list, no-results state, and browse error state.
- [X] T009 [US1] Extend `static/css/site.css` with matches-form and browse-result styling that matches the existing visual system.

**Checkpoint**: User Story 1 is fully functional and testable on its own.

---

## Phase 4: User Story 2 - View a Match Summary (Priority: P2)

**Goal**: Let visitors select a browse result and view a concise match summary based on the detail document.

**Independent Test**: Open one result from `/matches` and verify the detail route renders a readable summary from the backend `info` data plus a route back to browse results.

### Tests for User Story 2

- [X] T010 [P] [US2] Extend `tests/test_routes.py` with coverage for `GET /matches/<match_id>` success rendering.

### Implementation for User Story 2

- [X] T011 [US2] Add the `/matches/<match_id>` route to `app.py`.
- [X] T012 [US2] Create `templates/match_detail.html` with concise info-derived presentation and back-navigation.
- [X] T013 [US2] Add date-range formatting and summary presentation support through `matches_api.py` and template context.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Recover Gracefully from Backend Problems (Priority: P3)

**Goal**: Ensure the browse and detail pages remain useful when the upstream API fails or returns nothing.

**Independent Test**: Simulate upstream failure for browse and detail requests and verify rendered error states; simulate no results and verify a rendered empty state.

### Tests for User Story 3

- [X] T014 [P] [US3] Extend `tests/test_routes.py` with coverage for browse/detail upstream failure handling.

### Implementation for User Story 3

- [X] T015 [US3] Add browse-level error-state handling in `app.py` and `templates/matches.html`.
- [X] T016 [US3] Add detail-level error-state handling in `app.py` and `templates/match_detail.html`.
- [X] T017 [US3] Render a no-results state for successful browse calls returning no items.

**Checkpoint**: The feature remains usable under expected backend failure modes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, readability, and verification work across all stories.

- [X] T018 [P] Run the full pytest suite and fix any regressions in `tests/test_routes.py` or related feature files.
- [X] T019 Review templates and CSS for responsive behavior and visual consistency with the existing site.
- [X] T020 Document future extension readiness for API-driven option lists in the feature artifacts.

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup can begin immediately.
- Foundational depends on Setup and blocks all story work.
- User stories proceed in priority order, though some work within a phase can run in parallel.
- Polish depends on completion of the desired stories.

### User Story Dependencies

- US1 depends on Foundational only.
- US2 depends on Foundational and reuses the browse route output and integration helpers.
- US3 depends on US1 and US2 because it hardens the implemented browse and detail flows.

### Parallel Opportunities

- T004 and T005 can run in parallel once `matches_api.py` exists conceptually.
- T006 can run in parallel with T008 and T009 after the route shape is defined.
- T010 can run in parallel with T012 once detail-route behavior is agreed.
- T014 can run in parallel with T015 through T017 after route-level failure behavior is defined.

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational work.
2. Ship `/matches` as a fully server-rendered browse page.
3. Add the selected-match detail route.
4. Harden failure behavior and documentation.

### Agent-Friendly Slices

1. One agent can own `matches_api.py` and upstream-response shaping.
2. One agent can own route wiring in `app.py` and navigation changes in `content.py`.
3. One agent can own the templates and CSS additions.
4. One agent can own `tests/test_routes.py` updates and final verification.
