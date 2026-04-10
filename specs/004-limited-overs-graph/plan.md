# Implementation Plan: Limited Overs Innings Progress Graph

**Branch**: `004-limited-overs-graph` | **Date**: 2026-04-10 | **Spec**: `/specs/004-limited-overs-graph/spec.md`
**Input**: Feature specification from `/specs/004-limited-overs-graph/spec.md`

## Summary

Extend the existing match-detail flow from the cricket API feature so limited-overs matches (ODI, T20, IT20, ODM) render a run progression line chart beneath the existing scorecard. The plan fits the current Flask architecture by keeping data shaping in `matches_api.py`, route orchestration in `app.py`, presentation in `templates/match_detail.html`, and small interactive behavior in `static/js/match_detail.js`, with route-level verification in `tests/test_routes.py`.

## Technical Context

**Language/Version**: Python 3.14, Jinja2 templates, vanilla JavaScript  
**Primary Dependencies**: Flask, pytest (existing), browser-native SVG/DOM APIs for chart rendering  
**Storage**: N/A (derived view model from upstream match detail payload)  
**Testing**: pytest route tests plus focused helper tests for graph data shaping  
**Target Platform**: Server-rendered web app for modern desktop/mobile browsers  
**Project Type**: server-rendered web-service  
**Performance Goals**: Keep first render usable with scorecard content; graph model construction must not materially slow match-detail response for normal limited-overs payload sizes  
**Constraints**: Preserve existing `/matches/<match_id>` behavior; no client-side framework adoption; maintain responsive layout and keyboard-usable interactions  
**Scale/Scope**: One enhanced route, one backend helper extension, one template extension, one JS enhancement module update, one CSS extension, and targeted tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Primary page content remains server-rendered in Flask (`app.py` + Jinja templates).
- PASS: Enhancement is additive and keeps architecture simple (no separate frontend app).
- PASS: Responsive and accessible behavior is explicitly included in CSS/interaction tasks.
- PASS: Verification path includes route-level tests and manual responsive checks.
- PASS: Upstream dependency failure handling remains explicit and user-visible.

Post-design re-check:

- PASS: Design keeps API integration responsibilities in `matches_api.py` and avoids introducing new infrastructure layers.

## Project Structure

### Documentation (this feature)

```text
specs/004-limited-overs-graph/
├── checklists/
│   └── requirements.md
├── plan.md
└── spec.md
```

### Source Code (repository root)

```text
app.py
matches_api.py
static/
├── css/
│   └── site.css
└── js/
    └── match_detail.js
templates/
└── match_detail.html
tests/
└── test_routes.py
```

**Structure Decision**: Keep the existing single Flask app structure. Add graph data derivation helpers in `matches_api.py`, pass graph-ready data from `app.py`, render chart scaffolding in `templates/match_detail.html`, and progressively enhance interactions in `static/js/match_detail.js`.

## Implementation Phases

### Phase 0: Data and Behavior Alignment

- Confirm the exact upstream detail payload fields used by current scorecard parsing (`document.innings[].overs[].deliveries[]` and `wickets[]`) in `matches_api.py`.
- Define graph view-model shape (series points, over labels, wicket markers, tooltip payload) as a stable contract between backend helper and template/JS.

### Phase 1: Design Artifacts for Execution

- Capture data model notes for progression points and wicket markers.
- Capture a quickstart/manual verification flow for ODI, T20, and non-limited-overs cases.
- Capture lightweight route/view contract notes for chart rendering states: available, partial, unavailable.

### Phase 2: Incremental Delivery by User Story

- Deliver US1 (progression lines), then US2 (wicket markers/tooltips), then US3 (compatibility and fallback behavior), each independently testable.

## Discrete Agent Tasks

Each task below is intentionally small and independently implementable by an AI coding agent with a clear scope and completion signal.

1. **T001 - Add limited-overs classifier helper**
Scope: `matches_api.py`
Deliverable: Utility that determines if a match type is in {ODI, T20, IT20, ODM} using normalized comparison.
Independent completion check: Unit-style helper assertions or route test stubs show expected true/false outcomes.

2. **T002 - Build innings progression extractor**
Scope: `matches_api.py`
Deliverable: Helper that converts innings overs/deliveries into cumulative runs per over-group point list.
Independent completion check: Given a mocked innings payload, output includes one point per completed over with cumulative totals.

3. **T003 - Build wicket marker extractor**
Scope: `matches_api.py`
Deliverable: Helper that emits wicket marker records keyed to over group, including batter, bowler, and dismissal method where available.
Independent completion check: Mocked over with multiple wickets yields multiple marker records for the same over bucket.

4. **T004 - Compose graph view model**
Scope: `matches_api.py`
Deliverable: Public function that returns graph-ready data for all innings plus chart metadata and availability state.
Independent completion check: Function returns `available`, `partial`, or `unavailable` state with structured payload.

5. **T005 - Wire graph model into route context**
Scope: `app.py`
Deliverable: `/matches/<match_id>` route computes graph model and passes it to template alongside existing `summary` and `scorecard`.
Independent completion check: Existing route still renders on success and includes graph context object in template render call.

6. **T006 - Add chart section below scorecard**
Scope: `templates/match_detail.html`
Deliverable: New section placed beneath scorecard that conditionally renders chart container for qualifying matches and fallback messaging for partial/unavailable data.
Independent completion check: HTML shows chart section in the expected location without altering existing summary/scorecard blocks.

7. **T007 - Embed serialized graph payload safely**
Scope: `templates/match_detail.html`
Deliverable: Chart data exposed for JS consumption via `data-*` or JSON script block with safe escaping.
Independent completion check: Browser page source shows structured data payload when qualifying match data exists.

8. **T008 - Implement chart rendering logic**
Scope: `static/js/match_detail.js`
Deliverable: Render line graph with one line per innings and x-axis over groups/y-axis cumulative runs using existing page lifecycle.
Independent completion check: For supplied payload, chart appears with plotted points count matching expected overs.

9. **T009 - Implement wicket markers and tooltip interaction**
Scope: `static/js/match_detail.js`
Deliverable: Marker rendering for wickets, including multiple wickets in same over, with hover/focus tooltip details.
Independent completion check: Multiple markers for same over remain individually discoverable and show wicket details.

10. **T010 - Add graph styling and responsive behavior**
Scope: `static/css/site.css`
Deliverable: Styles for chart container, legend, markers, and tooltips that fit current design tokens and mobile layout.
Independent completion check: Chart remains readable at desktop and mobile widths without overlapping scorecard content.

11. **T011 - Add route tests for qualifying/non-qualifying behavior**
Scope: `tests/test_routes.py`
Deliverable: Tests verify limited-overs matches include graph section and non-qualifying matches do not require it.
Independent completion check: New tests pass with mocked summary/detail payloads.

12. **T012 - Add tests for wicket marker edge cases**
Scope: `tests/test_routes.py` and/or helper-level tests in `tests/`
Deliverable: Coverage for multiple wickets in the same over and missing optional wicket fields.
Independent completion check: Tests assert data survives into rendered/serialized chart payload.

13. **T013 - Add partial/unavailable graph state tests**
Scope: `tests/test_routes.py`
Deliverable: Tests for limited-overs matches with incomplete innings data showing graceful fallback messaging.
Independent completion check: Route remains `200` and scorecard still renders while graph fallback appears.

14. **T014 - Regression and integration verification**
Scope: `tests/test_routes.py`, manual browser checks
Deliverable: Run full test suite; verify summary, scorecard tabs, and new graph behavior together.
Independent completion check: `pytest` passes and manual checks confirm no regressions in existing match-detail interactions.

## Execution Order and Parallelization

- Sequential foundation: T001 -> T002 -> T003 -> T004 -> T005.
- Parallel after route wiring: T006 and T010 can proceed together; T008 can start once T007 defines payload contract.
- Parallel verification: T011, T012, and T013 can be implemented concurrently after T005-T007 stabilize.
- Final gate: T014 after all story tasks complete.

## Complexity Tracking

No constitution violations expected. The feature intentionally avoids extra frameworks and keeps logic inside existing Flask/Jinja/vanilla JS boundaries.

## Implementation Notes (post-execution)

The following decisions diverged from or extended the original plan during execution. Recorded for future reference.

### Python runtime version
Plan stated Python 3.14; actual runtime is Python 3.13.9. No impact on implementation — no 3.14-specific APIs were used.

### `get_graph_availability` state set
The plan described three return values: `available`, `partial`, `unavailable`. An early draft also returned `not_applicable` for non-limited-overs matches but this was corrected to `unavailable` during T015 to keep the state set consistent with the plan contract.

### `graph_model` context shape includes `is_limited_overs`
The route passes `graph_model` as `{"availability", "is_limited_overs", "series", "wickets"}`. The `is_limited_overs` boolean was added to allow the template to gate the entire progression section without re-deriving match type in Jinja. This was not enumerated in the plan but is consistent with the architecture.

### `_count_innings_with_data` helper
A private helper was introduced in T015 to count total innings vs innings with over-level data, enabling precise `partial` vs `available` discrimination. The plan's T004 described this outcome but did not prescribe the helper decomposition.

### `build_cumulative_runs_by_over` as a standalone public function
The plan's T002 described an innings extractor as internal to the view-model builder. During T006 it was extracted as a separate public function (`build_cumulative_runs_by_over`) to keep the cumulative-runs logic independently testable and reusable.

### Wicket marker payload fields
The plan described batter, bowler, and dismissal method. The implementation also carries `dismissal` (same value as `dismissal_method`), `index_in_over` (for same-over stacking offset in the SVG renderer), `innings_number`, `team`, `over`, and `cumulative_runs`. These are additive and do not conflict with the plan contract.

### Chart rendered as inline SVG string
The plan referenced browser-native SVG/DOM APIs. The implementation builds an SVG markup string via JS template literals and sets `innerHTML` on the chart host element. This is consistent with the "no client-side framework" constraint and does not require any build tooling.

### Task numbering
The plan's Discrete Agent Tasks are numbered T001–T014 (14 tasks). The actual `tasks.md` uses a phase-annotated 21-task structure (T001–T021) that expands the plan's tasks into smaller independently executable units. The mapping is consistent; the tasks.md breakdown simply provides finer granularity.
