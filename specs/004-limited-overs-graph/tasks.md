# Tasks: Limited Overs Innings Progress Graph

**Input**: Design documents from `/specs/004-limited-overs-graph/`  
**Prerequisites**: `plan.md`, `spec.md`  
**Tests**: Manual verification is required by the specification; automated test tasks are included only for final regression and route verification at the end.  
**Organization**: Tasks are grouped by user story to keep each increment independently implementable and reviewable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when tasks touch different files and have no unmet dependencies
- **[Story]**: User story label from `spec.md` (`[US1]`, `[US2]`, `[US3]`)
- Every task includes exact file paths

## Phase 1: Setup

**Purpose**: Confirm the current implementation surface and create the feature task artifact.

- [X] T001 Review existing match-detail rendering and scorecard shaping in `app.py`, `matches_api.py`, and `templates/match_detail.html`
- [X] T002 Review current match-detail interactions and styling in `static/js/match_detail.js` and `static/css/site.css`

---

## Phase 2: Foundational

**Purpose**: Establish the shared graph data contract and route plumbing required by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T003 Define limited-overs match classification and graph availability helpers in `matches_api.py`
- [X] T004 Define progression-series and wicket-marker view-model builders in `matches_api.py`
- [X] T005 Wire the graph view model into the `/matches/<match_id>` route in `app.py`

**Checkpoint**: Match detail route can supply a stable graph payload and availability state to the template.

---

## Phase 3: User Story 1 - Compare Innings Run Progression (Priority: P1) 🎯 MVP

**Goal**: Show a cumulative runs-by-over line graph beneath the existing scorecard for ODI, T20, IT20, and ODM matches.

**Independent Test**: Open a limited-overs match detail page and verify the page shows a graph beneath the scoresheet with one line per innings and one point per over group.

### Implementation for User Story 1

- [ ] T006 [US1] Build cumulative runs-by-over extraction for innings data in `matches_api.py`
- [ ] T007 [US1] Add the graph section and qualifying-match conditional rendering beneath the scorecard in `templates/match_detail.html`
- [ ] T008 [US1] Expose serialized graph data for the page in `templates/match_detail.html`
- [ ] T009 [US1] Render innings progression lines, axes, and over-grouped points in `static/js/match_detail.js`
- [ ] T010 [P] [US1] Add graph layout, legend, and responsive chart styling in `static/css/site.css`

**Checkpoint**: User Story 1 is functional and visually integrated without wicket-specific interactions.

---

## Phase 4: User Story 2 - Understand Wicket Context (Priority: P2)

**Goal**: Show wicket events on the progression graph with discoverable tooltip context, including multiple wickets in the same over.

**Independent Test**: Open a limited-overs match with wicket events and verify wicket indicators appear at the relevant over positions with tooltip details for each wicket.

### Implementation for User Story 2

- [ ] T011 [US2] Extract wicket marker payloads including batter, bowler, and dismissal method in `matches_api.py`
- [ ] T012 [US2] Add wicket-indicator markup hooks and tooltip container support in `templates/match_detail.html`
- [ ] T013 [US2] Render wicket markers and support multiple wickets in the same over in `static/js/match_detail.js`
- [ ] T014 [P] [US2] Add tooltip and wicket-marker styling in `static/css/site.css`

**Checkpoint**: User Stories 1 and 2 work together, with wicket context available on qualifying matches.

---

## Phase 5: User Story 3 - Preserve Existing Match Detail Experience (Priority: P3)

**Goal**: Keep the current match-detail experience intact for non-qualifying formats and incomplete data while preserving readability on desktop and mobile.

**Independent Test**: Verify non-limited-overs matches render without requiring the graph, and limited-overs matches with incomplete data show a clear fallback state while the existing scorecard still works.

### Implementation for User Story 3

- [ ] T015 [US3] Implement partial-data and unavailable-data graph states in `matches_api.py`
- [ ] T016 [US3] Render non-qualifying, partial, and unavailable graph messaging in `templates/match_detail.html`
- [ ] T017 [US3] Update client-side graph initialization to safely skip non-qualifying and unavailable states in `static/js/match_detail.js`
- [ ] T018 [P] [US3] Refine responsive spacing and fallback presentation for scorecard-plus-graph layouts in `static/css/site.css`

**Checkpoint**: All three user stories are independently usable and the existing detail page remains stable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, regression coverage, and plan-to-implementation consistency.

- [ ] T019 Add route-level regression coverage for qualifying, non-qualifying, multi-wicket, and partial-data cases in `tests/test_routes.py`
- [ ] T020 Run full verification for the feature through `tests/test_routes.py` and manual browser checks against `templates/match_detail.html`
- [ ] T021 Update `specs/004-limited-overs-graph/plan.md` if implementation decisions materially change task ordering or graph-state assumptions

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup can start immediately.
- Foundational depends on Setup and blocks all user story work.
- User Story 1 depends on Foundational completion.
- User Story 2 depends on User Story 1 graph scaffolding.
- User Story 3 depends on the shared graph model and integrates with User Story 1 behavior.
- Polish depends on the desired user stories being complete.

### User Story Dependencies

- **US1**: Depends only on Foundational tasks.
- **US2**: Depends on the graph payload and rendering introduced in US1.
- **US3**: Depends on shared graph-state plumbing from Foundational and the chart scaffolding from US1.

### Parallel Opportunities

- T010 can run in parallel with T009 after T007-T008 define the chart structure.
- T014 can run in parallel with T013 after T012 defines tooltip hooks.
- T018 can run in parallel with T016-T017 after graph fallback states are defined.
- T019 can begin once T015-T018 stabilize the final rendering contract.

---

## Parallel Example: User Story 1

```text
Task: "T009 [US1] Render innings progression lines, axes, and over-grouped points in static/js/match_detail.js"
Task: "T010 [P] [US1] Add graph layout, legend, and responsive chart styling in static/css/site.css"
```

---

## Parallel Example: User Story 2

```text
Task: "T013 [US2] Render wicket markers and support multiple wickets in the same over in static/js/match_detail.js"
Task: "T014 [P] [US2] Add tooltip and wicket-marker styling in static/css/site.css"
```

---

## Parallel Example: User Story 3

```text
Task: "T016 [US3] Render non-qualifying, partial, and unavailable graph messaging in templates/match_detail.html"
Task: "T018 [P] [US3] Refine responsive spacing and fallback presentation for scorecard-plus-graph layouts in static/css/site.css"
```

---

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational tasks.
2. Complete User Story 1 and verify the graph appears for a qualifying match.
3. Stop and validate MVP behavior before adding wicket interactions.

### Incremental Delivery

1. Add progression graph support in `matches_api.py`, `app.py`, `templates/match_detail.html`, and `static/js/match_detail.js`.
2. Add wicket markers and tooltips without changing the base graph contract.
3. Add fallback-state hardening and regression verification.

### Agent-Friendly Strategy

1. One agent can own `matches_api.py` data-shaping work.
2. One agent can own template and route integration across `app.py` and `templates/match_detail.html`.
3. One agent can own chart behavior and visual styling in `static/js/match_detail.js` and `static/css/site.css`.
4. One agent can own verification updates in `tests/test_routes.py` and final regression checks.