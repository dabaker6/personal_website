# Feature Specification: ACA Scaling Dashboard v2 — Enhanced Monitoring & Navigation

**Feature Branch**: `006-scaling-enhancements`  
**Created**: 2026-04-28  
**Status**: Draft  
**Input**: User improvements identified from v1 testing:
1. Continuous background polling of metrics throughout session
2. Send button reappearance after scaling event completes
3. Placeholder loading states on initial page load
4. Live queue depth updates during polling (already implemented in v1)
5. Navigation redesign with "Demo" section containing Cricket Data and Scaling
6. Eager polling start for chart data (not waiting for 202 response)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live Metrics Throughout Session (Priority: P1)

As a visitor monitoring a scaling event, I want the queue depth and replica count to update continuously while I'm viewing the page, so I can track the current state of the system at any moment, even before or after a scaling event submission.

**Why this priority**: Continuous visibility of system state is foundational to the monitoring experience. Users expect live metrics like a dashboard, not stale values from the initial page load. This applies to the entire session, not just during active scaling events.

**Independent Test**: Navigate to /scaling and observe metrics updating at regular intervals over time. Verify that queue depth and replica count panels refresh without requiring page reload or submission of messages. Confirm separate, slower polling interval for background updates vs. faster polling during active monitoring.

**Acceptance Scenarios**:

1. **Given** a visitor is on the /scaling page with no active scaling event, **When** 5 seconds elapse, **Then** the queue depth and replica count panels are updated with fresh values from the backend.
2. **Given** continuous background polling is active, **When** the visitor submits messages and monitoring begins, **Then** the polling interval switches to a faster rate without interruption.
3. **Given** an active monitoring session has completed, **When** metrics stop being updated at the fast polling rate, **Then** the page returns to the slower background polling interval.
4. **Given** the visitor navigates away from /scaling and returns, **When** the page reloads, **Then** background polling resumes with fresh state.

---

### User Story 2 - Graceful Initial Load with Placeholders (Priority: P1)

As a visitor arriving at the /scaling page, I want to see a responsive page that displays immediately with placeholder content, then the real metrics appear, so the page feels fast and responsive rather than blocking on backend API calls.

**Why this priority**: Page responsiveness and perceived performance directly impact user experience. Showing placeholders while loading reduces perceived latency and prevents the blank-page frustration. This is foundational UX for modern dashboards.

**Independent Test**: Navigate to /scaling and measure time to first visual render (placeholder visible) vs. time to actual metric values. Confirm placeholders are visually distinct and indicate loading state. Verify fallback to error state if metrics fail to load.

**Acceptance Scenarios**:

1. **Given** a visitor navigates to /scaling, **When** the page is requested, **Then** HTML with placeholder content is delivered within 500ms.
2. **Given** the page has rendered with placeholders, **When** the backend API call completes successfully, **Then** placeholders are replaced with actual metric values without page jank or flash.
3. **Given** the backend API fails, **When** the metrics request times out or returns an error, **Then** the error message replaces the placeholder with a user-friendly explanation.
4. **Given** placeholders are displayed, **When** viewed on mobile (375px), **Then** the layout is readable and does not overflow.

---

### User Story 3 - Resubmit Messages After Completion (Priority: P2)

As a visitor whose first scaling event has completed, I want the send message form to reappear so I can immediately submit another batch of messages without page navigation or confusion about whether I can submit again.

**Why this priority**: Users may want to run multiple scaling experiments in sequence. Restoring the send form after completion keeps the workflow fluid and discoverable—users see the button and naturally know they can use it again.

**Independent Test**: Submit messages and wait for the scaling event to complete (queue empties or timeout occurs). Verify the send form reappears in its initial state, allowing a new submission. Confirm the form is properly reset (previous values cleared, validation ready).

**Acceptance Scenarios**:

1. **Given** a scaling event is in progress, **When** the queue empties and monitoring stops, **Then** the send message form transitions from hidden to visible.
2. **Given** a scaling event has completed and the form is visible, **When** the visitor enters a new message count and submits, **Then** a new 202 success response initiates monitoring again.
3. **Given** the form reappears after completion, **When** the visitor views it on mobile, **Then** the form is fully interactive and the button is not obscured.

---

### User Story 4 - Eager Chart Data Collection (Priority: P1)

As a system observing scaling behavior, I want the backend to start collecting queue depth measurements immediately after a message submission is accepted, not waiting for a 202 success response, so the chart has data from the very moment scaling begins and users see a complete time series.

**Why this priority**: Data fidelity is crucial for a scaling demonstration. If measurements are delayed until the client confirms the 202, the user loses the earliest data points, and the chart starts partway through the event. Eager collection ensures no data is lost.

**Independent Test**: Submit messages and immediately check that queue depth readings are being accumulated. Verify the chart displays data starting from the moment after submission (elapsed ≈ 0ms), not from some later timestamp. Confirm no data loss if the 202 response is delayed.

**Acceptance Scenarios**:

1. **Given** a message submission POST request is accepted by the backend, **When** the backend begins polling the queue immediately, **Then** the first reading in the chart has elapsed_ms ≈ 0.
2. **Given** the client has not yet received the 202 response, **When** the backend is already collecting metrics, **Then** the first chart data point is captured and visible to the user (even if UI updates slightly after 202 arrives).
3. **Given** a complete scaling event from submission to queue-empty, **When** the visitor examines the chart, **Then** the chart shows measurements spanning the entire duration without gaps or missing early data.

---

### User Story 5 - Navigation Redesign: Demo Section with Submenus (Priority: P2)

As a visitor exploring the site, I want the navigation to feature a top-level "Demo" section containing both the Cricket Data explorer and the Scaling Dashboard as submenus, so I immediately understand that these are related demonstration features and can easily access either one without scrolling through an overwhelming nav menu.

**Why this priority**: Information architecture improves discoverability. Grouping related demos under a "Demo" umbrella makes the site's educational features more visible and organized. This is a UX/IA improvement that enhances navigation clarity.

**Independent Test**: Verify the nav menu displays "Demos" as a top-level item (desktop) or a collapsed menu (mobile). Expand/tap the Demo section and confirm both Cricket Data and Scaling Dashboard appear as submenus. Test on 375px mobile and 1280px desktop widths.

**Acceptance Scenarios**:

1. **Given** a visitor views the site on desktop, **When** the navigation header is visible, **Then** a "Demo" item appears at the top level alongside or above other main nav items (Home, About, Contact, Updates).
2. **Given** the visitor hovers or focuses on "Demos", **When** a submenu appears, **Then** both "Cricket Data" and "Scaling" are listed as clickable links.
3. **Given** a visitor on mobile (375px), **When** the navigation is opened, **Then** "Demo" appears as an expandable item that can be tapped to reveal the Cricket Data and Scaling links.
4. **Given** the visitor is on the Scaling page, **When** viewing the nav, **Then** the "Scaling" link in the Demo submenu is marked as active (highlighted/underlined).
5. **Given** the demo submenu is expanded on mobile, **When** the visitor selects Scaling, **Then** the page navigates and the submenu closes (or remains accessible for further navigation).

---

### User Story 6 - Live Queue Depth Metric Updates (Priority: P1)

As a visitor monitoring a scaling event, I want the queue depth metric panel to update live with each polling cycle, showing the most recent queue value, so I can immediately see how the queue is being processed without having to look at the chart.

**Why this priority**: The metric panel is the most visible element on the page. Users glance at it first before examining the chart. Live updates here provide immediate feedback and confidence that monitoring is active and working.

**Independent Test**: Submit messages and observe the queue depth number in the metric panel. Verify it updates every polling interval (same frequency as the chart). Confirm the value matches the latest data point on the chart.

**Acceptance Scenarios**:

1. **Given** active monitoring is in progress, **When** a poll completes and returns new queue data, **Then** the queue depth metric panel displays the new value within 100ms.
2. **Given** the queue is decreasing during a scaling event, **When** the visitor watches the queue depth panel, **Then** the number visibly counts down as polling occurs.
3. **Given** monitoring has completed (queue empty or timeout), **When** polling stops, **Then** the final queue depth value (0 or last observed) remains visible on the metric panel.

---

### Edge Cases

- What happens if background polling (slow interval) encounters an error while fast polling is active? (do not silently retry background polling errors during active monitoring—fast polling is the authoritative source. Resume background polling once active monitoring completes.)
- How does the page behave if the visitor submits messages twice in rapid succession? (Send button disables immediately on first click to prevent double-submission. Button re-enables only if an error occurs and 202 is not received. Once 202 is received, button remains disabled until the scaling event completes or an error occurs during monitoring.)
- What if the visitor closes or navigates away from the page during an active scaling event? (Monitoring stops; no state is persisted in the session. If the user returns to /scaling, background polling immediately shows the current backend state—queue depth and replica count as they exist now—so the dashboard always reflects reality.)
- How does eager chart polling interact with the send button being disabled? (Send button disables immediately on submit and remains disabled until completion or an error. Eager chart polling begins in parallel and continues independent of button state. Chart data collection is not blocked by button state; it proceeds as long as the message submission was accepted and monitoring is active.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST perform continuous background polling of queue depth and replica count at a configurable interval (separate environment variable from active-monitoring interval) throughout the entire user session on /scaling.
- **FR-002**: The system MUST display placeholder content on initial /scaling page load before backend metrics are fetched, providing immediate visual feedback.
- **FR-003**: The system MUST replace placeholders with real metric values once the initial API call completes, without page reload or visible jank.
- **FR-004**: The system MUST transition the send message form from hidden to visible when a scaling event completes (queue reaches zero or timeout threshold met).
- **FR-005**: The system MUST immediately begin collecting queue depth readings for the chart upon message submission acceptance, without waiting for a 202 HTTP response confirmation.
- **FR-006**: The system MUST update the queue depth metric panel with the latest value during each active-monitoring polling cycle.
- **FR-007**: The navigation menu MUST feature a top-level "Demos" section containing Cricket Data and Scaling as submenus, accessible on both desktop and mobile viewports.
- **FR-008**: The "Demo" submenu MUST expand/collapse on mobile with tap/click interaction and display all submenu items without overflow.
- **FR-009**: The active nav link indicator MUST highlight the current page (e.g., "Scaling" when on /scaling) within the Demos submenu hierarchy.
- **FR-010**: The background polling interval (when no active scaling event) MUST be configurable and typically slower than the active-monitoring polling interval, reducing backend load during idle periods.

### Key Entities

- **Polling Configuration**: Defines two separate polling intervals—`BACKGROUND_POLLING_INTERVAL_MS` (default ~5 seconds) for continuous metrics and `ACTIVE_POLLING_INTERVAL_MS` (default 1 second) for during-event monitoring.
- **Placeholder State**: Initial UI representation before backend data arrives; visually distinct from error or data states.
- **Navigation Structure**: Reorganized with "Demo" as a top-level category grouping Cricket Data and Scaling Dashboard.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The /scaling page displays initial HTML with placeholders within 500ms of request; users perceive the page as immediately responsive.
- **SC-002**: Queue depth and replica count metric panels update at least once every 5 seconds when no active scaling event (background polling).
- **SC-003**: Active monitoring polling runs at least 3x per second or faster, providing real-time chart updates throughout the scaling event.
- **SC-004**: Send form reappears within 500ms of a scaling event completing (queue empty or timeout).
- **SC-005**: Chart displays data points starting from elapsed_ms ≈ 0 (within 500ms of message submission).
- **SC-006**: Users can resubmit messages on the same /scaling page without page reload or navigation.
- **SC-007**: Navigation menu is fully navigable and responsive on both 375px mobile and 1280px desktop viewports.
- **SC-008**: "Demso" submenu opens/closes on mobile within 300ms with no layout shift.
- **SC-009**: Placeholder content is visually distinguishable from real data (e.g., gray background, "Loading..." indicator, or skeleton screen).

## Assumptions

- The background polling interval will default to ~5 seconds; active-monitoring polling will be at ~1 seconds (or user-configured per v1).
- Eager chart polling is performed server-side or via a separate client-side mechanism that begins immediately upon form submission.
- Placeholder design will use existing design tokens (colors, spacing, typography) to maintain visual consistency with the site.
- Mobile navigation (375px) will use a hamburger menu or slide-out drawer; desktop (1280px) will use a horizontal nav bar with submenu dropdowns.
- The "Demos" section name and grouping are treated as a site-wide IA change and may impact other docs or linked resources; these will be addressed in planning/implementation.
- Session state for background polling (e.g., stored pending submissions) is not persisted; if the user navigates away and returns, they see the current backend state as of that moment.
- Error handling for background polling failures is non-disruptive; failures do not interrupt active monitoring or user interaction.
