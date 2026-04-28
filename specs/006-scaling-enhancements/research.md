# Research: ACA Scaling Dashboard v2 Design Decisions

**Date**: 2026-04-28  
**Feature**: ACA Scaling Dashboard v2 Enhancements  
**Branch**: `006-scaling-enhancements`

## Overview

This document captures key design decisions made during v2 planning, documenting the rationale, alternatives considered, and implementation approach for each major feature area.

---

## 1. Background Polling Architecture

### Decision: Separate, Slower Background Polling Interval

**Chosen**: Two-tier polling system with independent intervals:
- **Background polling** (default 30 seconds): Continuous polling throughout session when no scaling event is active
- **Active monitoring** (default 1-3 seconds, inherited from v1): Fast polling during active scaling events

**Rationale**:
- Reduces backend load during idle periods when users are simply viewing the page
- Provides continuous visibility of system state without aggressive API calls
- Allows users to notice when a scaling event becomes necessary
- Separates concerns: background polling for awareness, active monitoring for real-time data collection

**Alternatives Considered**:
1. Single polling interval throughout (rejected: excessive backend load during idle periods)
2. Lazy polling on first page interaction (rejected: misses background state changes)
3. Server-sent events or WebSockets (rejected: adds complexity, conflicts with existing Flask + vanilla JS architecture)

**Implementation**:
- Environment variable `BACKGROUND_POLLING_INTERVAL_MS` (default ~30 seconds)
- Read from environment in `app.py` and passed to template as context variable
- JavaScript polls `/scaling/api/status` at this interval on page load
- Pauses during active monitoring (when queue_length > 0)
- Resumes after monitoring completes (queue_length === 0, timeout, or error)

**Client-Side State Management**:
- Background polling and active monitoring share the same `/scaling/api/status` endpoint
- Only one polling interval is active at a time (mutual exclusion via polling state flags)
- Readings from background polling are not accumulated into the chart (chart only exists during active monitoring)

---

## 2. Placeholder Design Approach

### Decision: CSS-Rendered Placeholders with Server-Side Markup

**Chosen**: Server-render placeholder HTML markup with CSS styling to simulate loading state. Real metrics fetched after page render via client-side API call and DOM replacement.

**Rationale**:
- Placeholders visible immediately (within first 500ms) before any API call completes
- No JavaScript required for initial visual feedback (progressive enhancement)
- Consistent with existing v1 server-rendered approach
- Easy to style to match real metric panels (same height, spacing)
- No layout shift when replacing placeholders with real values

**Alternatives Considered**:
1. Skeleton screens (large, heavy CSS frameworks) - rejected: adds complexity
2. Hardcoded placeholder values via JavaScript - rejected: requires JS for initial render
3. Deferred rendering until API returns - rejected: violates responsive UX goal (500ms target)
4. Placeholder as data attribute in template - rejected: requires JavaScript parsing

**Implementation**:
- Template renders placeholder `<div>` for each metric panel with:
  - Fixed height matching real metric panel (prevents layout shift)
  - Gray background or opacity indicator (visual distinction from data)
  - "Loading..." text or skeleton-like styling
  - Same DOM structure as real metrics (simplifies replacement logic)
- JavaScript on page load triggers fetch of real metrics
- Upon API response, replaces placeholder DOM content in-place without page reload
- No visible jank because placeholder and real metrics share same height/spacing

**Styling**:
- Placeholder divs have class `.placeholder` with:
  - Fixed min-height equal to real `.metric-value` size
  - Gray background (opacity 0.2–0.3) or striped pattern
  - Muted text color or "Loading..." pseudo-content
  - Same padding/margins as real panels
- Real metrics replace placeholder content via `.textContent = value` update

---

## 3. Eager Chart Polling

### Decision: Client-Side Immediate Polling on Form Submit

**Chosen**: JavaScript begins polling `/scaling/api/status` immediately on form submit, before waiting for 202 response. Polling runs in parallel with form submission request.

**Rationale**:
- Ensures first chart reading captures elapsed time ≈ 0 (within 500ms of submission)
- No data loss if 202 response is delayed by network or server processing
- Chart renders with complete time series from submission moment onward
- Client-side approach simpler and fits existing v1 architecture
- No server-side state or background jobs needed

**Alternatives Considered**:
1. Server-side background job polling ACA API on message acceptance - rejected: added complexity, server-side state management
2. Wait for 202 before starting chart polling - rejected: loses early data points, chart starts partway through event
3. Retroactive data backfill based on API timestamps - rejected: unreliable, still loses initial moments

**Implementation**:
- On form submit (in `submit` event handler), capture `monitoringStart = Date.now()`
- Initiate fetch POST to `/scaling/api/send` (as before)
- Immediately start polling loop via `setInterval(pollStatus, polling_interval_ms)`
- First poll executes within polling_interval_ms of form submit (e.g., 1–3 seconds)
- First reading records `elapsed_ms = Date.now() - monitoringStart` (likely ≈ 1000–3000ms)
- If 202 response arrives during polling, `startMonitoring()` transitions UI state (form hidden, chart visible)
- Chart accumulates readings regardless of 202 timing; UI updates reflect latest polling state

**Error Handling**:
- If form submission fails (400, 429, 500) before 202, polling continues briefly (respects timeout)
- User sees chart attempt to start, then sees error message
- Form re-enabled for retry

---

## 4. Navigation Restructure: Demo Section

### Decision: Top-Level "Demo" Section with Cricket Data and Scaling Submenus

**Chosen**: Reorganize site navigation to introduce "Demo" as a top-level category grouping Cricket Data and Scaling Dashboard as submenus.

**Rationale**:
- Improves discoverability of related demonstration features
- Reduces main navigation menu clutter by grouping related items
- Makes educational/demo intent clear to first-time visitors
- Sets precedent for future demo features (e.g., additional tutorials)
- Enhances information architecture clarity

**Scope**:
- Applies to `/scaling` and existing `/cricksheet` (Cricket Data) pages
- No impact on other pages (Home, About, Contact, Updates)
- Desktop (1280px): Horizontal navbar with hover/focus dropdown submenu
- Mobile (375px): Hamburger menu with tap-to-expand submenu drawer

**Alternatives Considered**:
1. Sidebar navigation (rejected: layout changes, reduced viewport space)
2. Keep flat nav with icon indicators (rejected: unclear grouping)
3. Separate demo-only page (rejected: forces intermediate navigation step)

**Implementation**:
- Modify `content.py` navigation structure:
  - Add "Demo" as top-level `{"label": "Demo", "slug": "demo"}` entry with children
  - Nest `{"label": "Cricket Data", "endpoint": "cricksheet", ...}` under Demo
  - Nest `{"label": "Scaling", "endpoint": "scaling", ...}` under Demo
  - Maintain active link state so current page link is highlighted in submenu
- Modify `templates/base.html`:
  - Add conditional rendering for submenu items (check for `children` in nav item)
  - Desktop: submenu appears on hover/focus of Demo item (CSS `:hover`, `:focus-within`)
  - Mobile: toggle class to show/hide submenu on tap (minimal JavaScript)
- CSS styling:
  - `.nav-submenu` div with `display: none` by default
  - On `.nav-item:hover` or `.nav-item.open`, show submenu with `display: block`
  - Mobile breakpoint (≤540px): submenu slides/fades in within 300ms
  - No layout shift; submenu positioned absolutely or uses flexbox with reserved space

---

## 5. Form Restoration State Machine

### Decision: Simple Toggle + Reset on Monitoring Completion

**Chosen**: After monitoring stops (queue reaches 0, timeout, or error), transition form from `hidden=true` to `hidden=false` and reset input values.

**Rationale**:
- Allows users to run multiple scaling experiments in sequence without page reload
- Simple state machine: form always visible except during active monitoring
- Clear signal to user that they can submit again (button is visible and enabled)
- Preserves chart and status message after monitoring stops (context remains)

**Alternatives Considered**:
1. Keep form hidden permanently after completion (rejected: forces page reload for re-submission)
2. Animate form appearance (rejected: adds complexity, not essential for UX)
3. Auto-hide after timeout (rejected: hides affordance, confuses user)

**Implementation**:
- Track form visibility state with `form.hidden` property (existing pattern)
- On monitoring start: `form.hidden = true; chartSection.hidden = false`
- On monitoring completion (all stop conditions):
  - `form.hidden = false; chartSection.hidden = false` (leave chart visible alongside form)
  - `countInput.value = ""; sendButton.disabled = false` (reset form state)
  - Preserve status message and chart for user review
- Existing validation and submission logic remains unchanged (form is stateless relative to scaling events)

---

## 6. Live Queue Depth Metric Updates

### Decision: Update Metric Panel on Every Poll Cycle

**Chosen**: During active monitoring, call `updateQueueDepth(value)` after each `/scaling/api/status` poll to update the metric panel with latest queue length.

**Rationale**:
- Most visible feedback to user (metric panel is primary visual element)
- Confidence signal that monitoring is active and responsive
- Value always matches latest chart data point (consistency)
- Simple to implement (reuses existing `updateReplicaCount()` pattern)

**Implementation**:
- Reuse existing `updateQueueDepth()` function (added in v1 per user request)
- Call in `pollStatus()` after pushing reading to array: `updateQueueDepth(queueLength)`
- Replica count also updated at same point: `updateReplicaCount(replicaCount)`
- Metric panels are targets via `data-queue-depth` and `data-replica-count` attributes
- No separate polling interval; metric updates at same frequency as chart polling

---

## 7. Background Polling Error Handling

### Decision: Silent Errors, Resume After Monitoring Completes

**Chosen**: If background polling encounters an error, log silently and suppress error display. Only fast polling errors are shown to user. Resume background polling once active monitoring completes.

**Rationale**:
- Background polling is non-critical for user task (awareness only)
- Error display would distract from active monitoring
- Fast polling during monitoring is authoritative; background polling is supplementary
- Automatic resumption ensures continuous visibility after scaling event

**Implementation**:
- Background polling `.catch()` block logs error to console (silent from user perspective)
- No user-facing error message shown for background polling failures
- Active monitoring polling errors are shown in status message (user-facing, important)
- After monitoring stops, background polling resets and starts fresh
- Each failed background poll schedules next attempt at `background_polling_interval_ms`

---

## 8. Configuration & Defaults

| Configuration | Default | Environment Variable | Purpose |
|---------------|---------|----------------------|---------|
| Background polling interval | 5000 ms | `BACKGROUND_POLLING_INTERVAL_MS` | Polling frequency when idle |
| Active monitoring polling | 1000 ms (v1) | `POLLING_INTERVAL_MS` | Polling frequency during scaling event |
| Max monitoring duration | 300 s | `MAX_MONITORING_SECONDS` | Stop polling if queue doesn't clear |
| Zero replica timeout | 60 s | `ZERO_REPLICA_TIMEOUT_SECONDS` | Stop if replicas don't recover |
| Min messages | 1 | `MIN_MESSAGES` | Validation constraint |
| Max messages | 5000 | `MAX_MESSAGES` | Validation constraint |

**Rationale for defaults**:
- 5s background interval: noticeable state changes without excessive backend load
- 1s active monitoring: borrowed from v1 (user-tested, provides real-time feel)
- 300s max monitoring: 5 minutes is reasonable scaling window for demo purposes
- 60s zero-replica timeout: sufficient for transient scaling to recover
- Min/max messages: borrowed from v1 (user-tested range)

---

## 9. Technology Stack Decisions

### Preserved from v1
- **Flask** for routing and server-side rendering
- **Jinja2** templates for HTML generation
- **Vanilla JavaScript** (IIFE pattern) for client-side polling and chart rendering
- **stdlib `urllib`** for ACA API HTTP calls (no new dependencies)
- **pytest** for route and unit tests

### Why No New Dependencies
- Placeholder styling is pure CSS (no skeleton framework)
- Chart rendering is inline SVG (no charting library)
- Navigation dropdowns are CSS + minimal JS (no UI framework)
- All features implement as progressive enhancements on v1 foundation

---

## Conclusion

All v2 decisions are layered on top of v1 without breaking changes or architectural departures. The two-tier polling, placeholders, eager polling, and navigation restructure are implemented using the same patterns and technologies as v1, ensuring consistency and maintainability.

The research phase is complete. Proceed to implementation with confidence that design decisions have been thoroughly evaluated and documented.
