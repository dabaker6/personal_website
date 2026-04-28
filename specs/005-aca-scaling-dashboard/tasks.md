# Tasks: ACA Scaling Dashboard

**Input**: Design documents from `/specs/005-aca-scaling-dashboard/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story. Each phase delivers an independently testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to ([US1], [US2], [US3])
- **[x]**: Task complete

---

## Phase 1: Setup (ACA API Module)

**Purpose**: Create the ACA scaling API client module that all routes depend on.

- [x] T001 Create aca_scaling_api.py with AcaScalingApiError, get_revision_name(), get_replica_count(), get_queue_length(), send_messages() using stdlib urllib — reads ACA_API_BASE_URL from environment; 429 response parses active_message_count from body

**Checkpoint**: `import aca_scaling_api` succeeds; all four functions raise AcaScalingApiError with correct status_code; 429 populates active_message_count.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Route registration and navigation wiring that all user stories depend on. No user story template or JS work can be verified until this phase is complete.

**⚠️ CRITICAL**: Complete before any user story implementation.

- [x] T002 Add scaling page content dict and navigation entry `{"label": "Scaling", "endpoint": "scaling", "slug": "scaling"}` to SITE_CONTENT in content.py
- [x] T003 Add GET /scaling route to app.py: calls get_revision_name(), get_replica_count(), get_queue_length() from aca_scaling_api; passes initial metrics and ScalingConfig values (polling_interval_ms, max_monitoring_seconds, zero_replica_timeout_seconds, min_messages=1, max_messages=5000) read from environment with defaults to templates/scaling.html; catches AcaScalingApiError and renders template with error_message; always returns 200 OK
- [ ] T004 [P] Add GET /scaling/api/status route to app.py: calls get_revision_name(), get_replica_count(), get_queue_length(); returns JSON {"queue_length": int, "replica_count": int, "revision_name": str} on success; returns JSON {"error": str, "code": str} with HTTP 500 on AcaScalingApiError; no HTML returned
- [ ] T005 [P] Add POST /scaling/api/send route to app.py: reads count from JSON body; validates 1 ≤ count ≤ 5000 (returns 400 JSON on failure); calls send_messages(count); returns 202 JSON {"message_count": int} on success; returns 429 JSON {"error": str, "queue_length": int} when AcaScalingApiError.status_code == 429; returns 500 JSON {"error": str} on other failures

**Checkpoint**: GET /scaling returns 200 HTML; /scaling/api/status returns JSON; /scaling/api/send returns correct status codes for valid, invalid, and 429 inputs.

---

## Phase 3: User Story 1 — View Current Scaling State (Priority: P1) 🎯 MVP

**Goal**: Visitor navigates to /scaling and immediately sees current replica count and queue depth in server-rendered HTML.

**Independent Test**: Navigate to /scaling with ACA API mocked; confirm both metric panels display values and the Scaling nav link is active. Page usable on mobile (375px).

### Implementation for User Story 1

- [ ] T006 [US1] Create templates/scaling.html extending base.html: page intro section (eyebrow, headline from page context); two labelled metric panels — queue depth (`data-queue-depth`) showing `{{ queue_depth }}` and replica count (`data-replica-count`) showing `{{ replica_count }}`; error fallback rendered when `error_message` is set; `page_name="scaling"` wired for active nav state

**Checkpoint**: GET /scaling renders both metric panels with server-side values; error fallback renders when error_message provided; Scaling nav link is marked active.

---

## Phase 4: User Story 2 — Send Messages and Trigger Scaling (Priority: P2)

**Goal**: Visitor enters a message count, submits it, sees a distinct success/busy/error response, and the dashboard transitions to monitoring mode on success.

**Independent Test**: Enter a valid count → submit → confirm 202 transitions UI to monitoring state. Enter 0 → confirm inline validation error. Enter a count when queue is active → confirm 429 message shows queue count.

### Implementation for User Story 2

- [ ] T007 [US2] Add to templates/scaling.html: dashboard container element with data attributes — `data-polling-interval-ms`, `data-max-monitoring-seconds`, `data-zero-replica-timeout-seconds`, `data-min-messages`, `data-max-messages` — all populated from template context; message submission form with number input (min/max from context) and clearly labelled send button; hidden chart section (`data-chart-section`); monitoring status message area (`data-status-message`); `<script src="{{ url_for('static', filename='js/scaling.js') }}"></script>` at end of block
- [ ] T008 [US2] Create static/js/scaling.js as IIFE: reads all config from container data attributes on DOMContentLoaded; validates message count on submit (rejects outside 1–5000 with inline error, no API call); POSTs JSON {"count": N} to /scaling/api/send; on 202 — shows success status message and transitions to monitoring state; on 400 — shows inline validation error; on 429 — shows distinct "Queue still active, N messages remaining" message with count from response queue_length; on 500 — shows error message; disables submit button during request

**Checkpoint**: Count=0 and count=5001 show inline errors without API calls; valid count + 202 response sets monitoring state; 429 response displays correct queue count in status area.

---

## Phase 5: User Story 3 — Observe Live Scaling Behaviour (Priority: P3)

**Goal**: After message submission, queue depth is plotted over time as a live chart, replica count updates with each poll, and monitoring stops correctly on all end conditions with all data preserved.

**Independent Test**: Submit valid count → wait two polling cycles → confirm chart gains data points and replica count panel updates. Confirm chart and data persist on: queue=0, timeout, polling error, and zero-replica timeout.

### Implementation for User Story 3

- [ ] T009 [US3] Add polling loop to static/js/scaling.js: after monitoring starts, polls GET /scaling/api/status every polling_interval_ms milliseconds; updates data-replica-count panel with each response; accumulates {elapsed_ms, queue_length} readings in array; stops polling (preserving all display) when queue_length === 0 (normal end), elapsed_ms ≥ max_monitoring_seconds * 1000 (shows timeout notice), or fetch error received (shows error message)
- [ ] T010 [P] [US3] Add queue depth chart rendering to static/js/scaling.js: after each poll adds a reading, renders or updates an inline SVG in data-chart-section — x-axis is elapsed seconds, y-axis is queue depth, points connected by a line, one point per reading; reveals data-chart-section on first reading; single-reading case renders without error; chart container preserved and visible after polling stops regardless of stop condition
- [ ] T011 [P] [US3] Add zero-replica timeout logic to static/js/scaling.js: when poll returns replica_count === 0, starts internal timer set to zero_replica_timeout_seconds; if replica_count recovers above zero before timer fires, cancels timer and continues monitoring; if timer fires, stops polling, shows error message "Replicas did not recover — scaling may have stalled", preserves all captured chart data on screen

**Checkpoint**: Two poll cycles update replica count and grow chart; queue=0 stops polling with chart preserved; timeout notice appears after max duration; zero-replica timer cancels on recovery; error mid-session preserves chart.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Styling, tests, and full verification — applies across all user stories.

- [ ] T012 [P] Add dashboard styles to static/css/site.css: metric panels (queue depth, replica count) fitting existing info-card design tokens; submit form controls; chart SVG container; monitoring status message; error states; responsive at 375px and 1280px — panels and chart do not overflow
- [ ] T013 [P] Add route and proxy endpoint tests to tests/test_routes.py: GET /scaling success (both panels in HTML, active nav) and ACA error (error message rendered, still 200); GET /scaling/api/status success JSON and 500 error JSON; POST /scaling/api/send 202 success, 400 out-of-range, 429 with queue_length field, 500 ACA error — all with mocked aca_scaling_api functions
- [ ] T014 [P] Create tests/test_aca_scaling_api.py: unit tests for all four aca_scaling_api functions with mocked urllib responses — get_revision_name() success and 404; get_replica_count() success and 500; get_queue_length() success and 500; send_messages() 202 success, 400, 429 with active_message_count parsed from response body, 500, and URLError connection failure
- [ ] T015 Run full pytest suite and verify against quickstart.md scenarios: initial page load, valid submission + monitoring, 429 flow, ACA unavailable error state, responsive layout at mobile and desktop widths

**Checkpoint**: All tests pass; quickstart.md scenarios verified manually; no regressions in existing routes.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Complete ✓ — T001 done
- **Phase 2 (Foundational)**: Depends on T001 — BLOCKS all user stories
  - T002 and T003+T004+T005 can run in parallel once T001 is done
- **Phase 3 (US1)**: Depends on Phase 2 completion (T002, T003, T004, T005)
- **Phase 4 (US2)**: Depends on Phase 3 completion (T006 provides HTML structure for T007)
- **Phase 5 (US3)**: Depends on Phase 4 completion (T008/T009 provide polling foundation)
  - T010 and T011 can run in parallel after T009
- **Phase 6 (Polish)**: T012, T013, T014 can all run in parallel after Phase 5; T015 runs last

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational phase only
- **US2 (P2)**: Depends on US1 HTML structure (T006) for T007 template additions
- **US3 (P3)**: Depends on US2 JS foundation (T008) for polling and chart extensions

### Parallel Opportunities

- T004 and T005 are parallel after T001 (different endpoints, same file — coordinate if working with multiple agents)
- T010 and T011 are parallel after T009 (both extend scaling.js but touch distinct functions)
- T012, T013, T014 are all parallel in Phase 6

---

## Parallel Example: Phase 2 Foundational

```text
After T001 complete:
  Sequential: T002 (content.py — must precede T003 route wiring)
  Then parallel: T003, T004, T005 (all in app.py — different functions, coordinate edits)
```

## Parallel Example: Phase 5 User Story 3

```text
After T009 (polling loop) complete:
  Parallel: T010 (chart rendering) + T011 (zero-replica timeout)
  Both add new functions to scaling.js without touching the polling loop itself
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Phase 1 ✓ — T001 done
2. Phase 2 — T002 → T003, T004, T005 (parallel)
3. Phase 3 — T006
4. **STOP and VALIDATE**: navigate to /scaling, confirm server-rendered metrics and active nav link
5. Add T012 (CSS) for presentable MVP

### Incremental Delivery

1. Phase 1 ✓ + Phase 2 → Foundational ready
2. Phase 3 (US1) → Server-rendered dashboard, verify independently → MVP
3. Phase 4 (US2) → Submission + monitoring state, verify independently
4. Phase 5 (US3) → Live chart + polling, verify independently
5. Phase 6 (Polish) → Tests + CSS + full verification

---

## Notes

- [P] tasks = different files or non-overlapping functions; safe to work in parallel
- [Story] label maps each task to its user story for traceability
- T001 is pre-marked complete; pick up from T002
- T004 and T005 both edit app.py — sequence them or merge edits carefully if working with multiple agents
- Commit after each phase checkpoint before moving to the next
- Run `pytest` after Phase 6 to confirm all tests pass and no regressions
