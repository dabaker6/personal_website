# Implementation Plan: ACA Scaling Dashboard

**Branch**: `005-aca-scaling-dashboard` | **Date**: 2026-04-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-aca-scaling-dashboard/spec.md`

## Summary

Add a `/scaling` page to the personal website that demonstrates Azure Container App queue-based scaling. The page renders current replica count and queue depth server-side on first load, then uses vanilla JS polling to plot queue depth over time and update the replica count while a scaling event is in progress. Flask proxy endpoints (`/scaling/api/status` and `/scaling/api/send`) insulate the browser from the upstream ACA scaling API. All configurable timeouts and the polling interval are passed from server configuration via template data attributes. Follows the same Flask + Jinja + stdlib urllib + vanilla JS IIFE architecture established in the existing codebase.

## Technical Context

**Language/Version**: Python 3.13, Jinja2 templates, vanilla JavaScript  
**Primary Dependencies**: Flask (existing), `urllib` stdlib for ACA API calls, pytest (existing), python-dotenv (existing)  
**Storage**: N/A — queue depth readings accumulated in JS memory for the session; not persisted across navigations  
**Testing**: pytest route tests (`tests/test_routes.py`) plus new API module unit tests (`tests/test_aca_scaling_api.py`)  
**Target Platform**: Server-rendered web app for modern desktop/mobile browsers  
**Project Type**: server-rendered web-service  
**Performance Goals**: Initial page load delivers current metrics in the first server response; keep first render fast; polling interval chosen to make scaling changes visible within a reasonable time  
**Constraints**: No client-side framework; follow existing IIFE + data attribute JS pattern; no secrets in source; ACA API base URL from environment variable; preserve all existing route and rendering behavior  
**Scale/Scope**: One new primary route, two JSON proxy endpoints, one new API module, one new template, one new JS module, CSS additions, and targeted tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Primary page (`/scaling`) is server-rendered by Flask and returns usable HTML including current metric values on the first server response (Principle I).
- PASS: Progressive client-side polling enhances the experience but the initial metrics are in the server-rendered HTML, so core content is accessible without JavaScript (Principle III).
- PASS: Feature is implemented entirely within the existing Flask + Jinja + vanilla JS architecture; no client-side framework or additional frontend application layer (Principle III).
- PASS: Responsive and accessible behavior is explicitly planned in the template and CSS tasks; both metric panels and the chart container are verified at mobile and desktop widths (Principle II).
- PASS: Verification path includes route tests, API module tests, and a documented manual quickstart flow (Principle IV).
- PASS: ACA API failures during initial load produce a clear, usable degraded HTML response; mid-session polling errors stop polling and preserve already-captured data — no raw error details exposed (Principle V, FR-011).
- PASS: ACA API base URL and all configurable timing values are read from environment variables; nothing sensitive is committed (Principle V).

Post-design re-check:

- PASS: Flask proxy endpoints keep ACA API integration in `aca_scaling_api.py`; routing and orchestration stay in `app.py`; no business logic leaks into templates or JS.

## Project Structure

### Documentation (this feature)

```text
specs/005-aca-scaling-dashboard/
├── checklists/
│   └── requirements.md
├── contracts/
│   └── scaling-routes.md    ← Phase 1 output
├── plan.md                  ← this file
├── spec.md
├── research.md              ← Phase 0 output
├── data-model.md            ← Phase 1 output
├── quickstart.md            ← Phase 1 output
└── tasks.md                 ← Phase 2, created by /speckit-tasks
```

### Source Code (repository root)

```text
aca_scaling_api.py          ← new: ACA API client module
app.py                      ← modified: /scaling, /scaling/api/status, /scaling/api/send routes
content.py                  ← modified: navigation entry + scaling page content
static/
├── css/
│   └── site.css            ← modified: dashboard metric panel, chart, and form styles
└── js/
    └── scaling.js          ← new: dashboard polling, chart rendering, timeout logic
templates/
└── scaling.html            ← new: dashboard page template
tests/
├── test_routes.py          ← modified: new route and proxy endpoint tests
└── test_aca_scaling_api.py ← new: API module unit tests
```

**Structure Decision**: Single Flask app with the new feature following the existing module decomposition — API client logic in a dedicated module (`aca_scaling_api.py`), route orchestration in `app.py`, content and navigation registration in `content.py`, presentation in `templates/scaling.html`, progressive enhancement in `static/js/scaling.js`.

## Implementation Phases

### Phase 0: Research and Decision Alignment

- Confirm HTTP client pattern matches existing `matches_api.py` (stdlib `urllib`; no new dependency needed).
- Confirm configurable values (polling interval, max monitoring duration, zero-replica timeout) are passed via environment variables and embedded as template data attributes for JS consumption.
- Confirm the 429 response body from the ACA API includes `message` containing the active message count, matching the spec requirement to surface that count to the visitor.

### Phase 1: Design Artifacts

- Capture data model for entities: `ScalingStatus`, `ScalingConfig`, `QueueDepthReading`, and `NavigationItem`.
- Define Flask proxy API contracts: `GET /scaling`, `GET /scaling/api/status`, `POST /scaling/api/send`.
- Document quickstart verification flow covering: initial page load, valid submission with monitoring, 429 flow, zero-replica timeout simulation, and error mid-session.

### Phase 2: Incremental Delivery by User Story

- Deliver US1 (initial metrics display), then US2 (message submission + 429 handling), then US3 (live chart and polling), each independently testable.

## Discrete Agent Tasks

Each task is intentionally small and independently implementable by an AI coding agent with a clear scope and completion signal.

1. **T001 - Create aca_scaling_api.py**  
   Scope: `aca_scaling_api.py` (new file)  
   Deliverable: `AcaScalingApiError` exception class with `status_code` and optional `active_message_count` fields; `get_revision_name()`, `get_replica_count(revision_name)`, `get_queue_length()`, `send_messages(count)` functions; reads `ACA_API_BASE_URL` from environment. `send_messages` raises `AcaScalingApiError(status_code=429, active_message_count=N)` when ACA returns 429, parsing the count from the response body `message` field.  
   Independent completion check: Module importable; functions raise `AcaScalingApiError` with correct `status_code` in unit tests with mocked HTTP responses; 429 path populates `active_message_count`.

2. **T002 - Add /scaling route to app.py**  
   Scope: `app.py`  
   Deliverable: `GET /scaling` route that calls `get_revision_name()`, `get_replica_count()`, and `get_queue_length()` from `aca_scaling_api`; passes initial metric values and config values (`polling_interval_ms`, `max_monitoring_seconds`, `zero_replica_timeout_seconds`, `min_messages=1`, `max_messages=5000`) to `templates/scaling.html`. Catches `AcaScalingApiError` and renders the template with an `error_message` context variable; page still returns `200 OK`.  
   Independent completion check: Route renders successfully with mocked API module; error path renders gracefully with error context and `200` status.

3. **T003 - Add /scaling/api/status JSON endpoint**  
   Scope: `app.py`  
   Deliverable: `GET /scaling/api/status` JSON endpoint; fetches revision name, replica count, and queue length; returns `{"queue_length": int, "replica_count": int, "revision_name": str}` on success; returns `{"error": str, "code": str}` with a `500` status on failure. No HTML is returned.  
   Independent completion check: Endpoint returns valid JSON `200` on success and JSON `500` on `AcaScalingApiError`; no HTML content-type in either case.

4. **T004 - Add /scaling/api/send JSON endpoint**  
   Scope: `app.py`  
   Deliverable: `POST /scaling/api/send` JSON endpoint; reads `count` from JSON body; validates `1 ≤ count ≤ 5000`; proxies to `send_messages(count)`; returns `202 {"message_count": int}` on success; `400 {"error": str}` for out-of-range input; `429 {"error": str, "queue_length": int}` when ACA returns 429 (using `active_message_count` from the exception); `500 {"error": str}` for other ACA failures.  
   Independent completion check: Returns 400 for count=0 and count=5001; returns 429 JSON with `queue_length` field matching the mocked exception; returns 202 on success.

5. **T005 - Add scaling page to content.py**  
   Scope: `content.py`  
   Deliverable: Add `{"label": "Scaling", "endpoint": "scaling", "slug": "scaling"}` to the `navigation` list; add a `"scaling"` entry to `pages` with `title`, `meta_description`, `eyebrow`, `headline`, and `intro` fields consistent with the site's voice.  
   Independent completion check: Existing navigation entries unchanged; `/scaling` link appears in the rendered nav bar; `get_page(site_content, "scaling")` returns the new page dict.

6. **T006 - Create templates/scaling.html with initial panels and form**  
   Scope: `templates/scaling.html` (new file)  
   Deliverable: Template extending `base.html`; page intro section; two metric panels with server-rendered initial values — queue depth (`queue_depth`) and replica count (`replica_count`) — each with a clearly labelled heading; message submission form with a number input (rendered with `min` and `max` from template context) and a clearly labelled send button; error state fallback shown when `error_message` is set in context.  
   Independent completion check: Template renders without Jinja errors; metric panels show initial values; form input has correct `min`/`max` attributes; error fallback renders when `error_message` is provided.

7. **T007 - Add chart section and data attributes to templates/scaling.html**  
   Scope: `templates/scaling.html`  
   Deliverable: Dashboard container element with `data-*` attributes exposing all config values (`data-polling-interval-ms`, `data-max-monitoring-seconds`, `data-zero-replica-timeout-seconds`, `data-min-messages`, `data-max-messages`) for JS consumption; chart section element (`data-chart-section`) initially hidden; monitoring status message area (`data-status-message`); replica count panel marked with `data-replica-count` for JS update; queue depth panel marked with `data-queue-depth`.  
   Independent completion check: Rendered HTML source contains all `data-*` config attributes with correct values; `data-chart-section` and `data-status-message` elements are present; `data-replica-count` and `data-queue-depth` target elements are present.

8. **T008 - Create scaling.js with validation and submission**  
   Scope: `static/js/scaling.js` (new file, IIFE pattern matching existing JS)  
   Deliverable: Reads config from container data attributes on `DOMContentLoaded`; validates message count on form submit (rejects values outside 1–5000, shows inline error, does not call API); POSTs to `/scaling/api/send` with `{count}`; handles responses — 202: transition to monitoring state, 400: show validation error inline, 429: show "queue still active, N messages remaining" message, 500: show error; disables submit button during request.  
   Independent completion check: Submitting count=0 or count=5001 shows inline error without calling API; submitting a valid count and receiving 202 sets monitoring state; 429 response shows the correct queue count in the status message.

9. **T009 - Add polling loop to scaling.js**  
   Scope: `static/js/scaling.js`  
   Deliverable: After monitoring starts, polls `GET /scaling/api/status` at `polling_interval_ms`; updates `data-replica-count` panel; accumulates `{elapsed_ms, queue_length}` readings; stops polling with display preserved on: `queue_length === 0` (normal end), `elapsed_ms ≥ max_monitoring_seconds * 1000` (timeout, show notice), error response (show error). All captured readings remain visible after polling stops.  
   Independent completion check: After two simulated poll responses, replica count updates and readings array contains two entries; each stop condition halts polling and leaves the chart container visible.

10. **T010 - Add queue depth chart to scaling.js**  
    Scope: `static/js/scaling.js`  
    Deliverable: After each poll adds a reading, renders or updates an inline SVG in `data-chart-section`: x-axis is elapsed time (seconds), y-axis is queue depth, one plotted point per reading, points connected by a line. Reveals `data-chart-section` on first reading. Single-reading case renders a point without error.  
    Independent completion check: With one reading, SVG renders a single point without throwing; with three readings, the connecting line has two segments and x-axis spans correct elapsed range.

11. **T011 - Add zero-replica timeout to scaling.js**  
    Scope: `static/js/scaling.js`  
    Deliverable: When a poll returns `replica_count === 0`, starts an internal timer set to `zero_replica_timeout_seconds`. If `replica_count` recovers above zero before the timer fires, cancels the timer. If the timer fires, stops polling, shows an error message ("Replicas did not recover — scaling may have stalled"), preserves all captured data on screen.  
    Independent completion check: Simulating zero then above-zero cancels the timer; simulating persistent zero past the timeout triggers the error message and stops polling.

12. **T012 - Add dashboard styles to site.css**  
    Scope: `static/css/site.css`  
    Deliverable: Styles for metric panels (queue depth, replica count cards fitting existing `.info-card` / design token patterns), the submit form controls, chart SVG container, monitoring status message, and error states. Responsive at 375px and 1280px: panels and chart do not overflow; text remains readable.  
    Independent completion check: At both mobile and desktop widths, metric panels and chart container are readable and correctly contained within the page layout.

13. **T013 - Add route and proxy endpoint tests to test_routes.py**  
    Scope: `tests/test_routes.py`  
    Deliverable: Tests for `GET /scaling` (success, ACA error renders gracefully, navigation active state); `GET /scaling/api/status` (200 success JSON, 500 error JSON); `POST /scaling/api/send` (202 success, 400 out-of-range, 429 with `queue_length`, 500 ACA error). All tests mock `aca_scaling_api` functions.  
    Independent completion check: All new tests pass independently of whether the real ACA API is available; existing tests remain green.

14. **T014 - Create test_aca_scaling_api.py**  
    Scope: `tests/test_aca_scaling_api.py` (new file)  
    Deliverable: Unit tests for each function in `aca_scaling_api.py` with mocked `urllib` responses: `get_revision_name()` success and 404; `get_replica_count()` success and 500; `get_queue_length()` success and 500; `send_messages()` 202 success, 400 error, 429 with `active_message_count` parsed from response body, 500 error, and connection timeout.  
    Independent completion check: All tests pass with patched HTTP layer; 429 test asserts `AcaScalingApiError.active_message_count` matches value in mocked response body.

## Execution Order and Parallelization

- Sequential foundation: T001 → (T002, T003, T004 in parallel) → T005 → T006 → T007
- Parallel after T001: T014 can begin immediately once the module interface is defined
- JS layer sequential: T008 → T009 → T010 and T011 in parallel (both extend the polling loop independently)
- T012 (CSS) can proceed in parallel with any JS task once T006/T007 establish the HTML structure
- T013 (route tests) can proceed in parallel with T012/T008 once T002–T004 are complete
- Final gate: run full `pytest` suite and manual quickstart verification after all tasks complete

## Complexity Tracking

No constitution violations. The feature intentionally avoids client-side frameworks, keeps API integration in a dedicated module, and uses the existing Flask/Jinja/vanilla JS architecture throughout.
