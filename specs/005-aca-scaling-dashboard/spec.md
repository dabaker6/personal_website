# Feature Specification: ACA Scaling Dashboard

**Feature Branch**: `005-aca-scaling-dashboard`  
**Created**: 2026-04-27  
**Status**: Draft  
**Input**: User description: "I want to create a new feature that demonstrates azure container app scaling. The replica count, and queue length should be displayed to the user as a dashboard that could be extended further at a later date. When the user navigates to the page the current replicas should be displayed, and there be a button with an input for the number of messages to send to the queue. The input should be sanitised for a min and max allowed number of messages. When the user clicks to send the messages I would like the api queue length and replicas to be polled and the queue length to be plotted against time updated as the api is polled, with the replica count also updated."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Current Scaling State (Priority: P1)

As a visitor to the personal website, I want to navigate to the scaling dashboard and immediately see the current number of running container instances and the number of messages waiting in the queue, so I can understand the live state of the Azure Container App scaling demonstration.

**Why this priority**: The dashboard's core value is displaying live scaling metrics. Without this, no further interaction is meaningful. A working initial state view is the minimum viable version of the feature.

**Independent Test**: Can be fully tested by navigating to the scaling dashboard page and confirming that both the replica count and queue depth are visible and reflect values retrieved from the scaling service. No user interaction beyond page load is required.

**Acceptance Scenarios**:

1. **Given** a visitor navigates to the scaling dashboard, **When** the page finishes loading, **Then** the current replica count and current queue depth are both displayed in clearly labelled panels.
2. **Given** a visitor navigates to the scaling dashboard while the scaling service is unavailable, **When** the page finishes loading, **Then** an informative error message is shown in place of the metric values, and the page remains usable.
3. **Given** a visitor views the dashboard on a mobile device, **When** the page loads, **Then** both metric panels are readable and the layout does not overflow or overlap.

---

### User Story 2 - Send Messages and Trigger Scaling (Priority: P2)

As a visitor, I want to enter a number of messages to send and submit them via the dashboard, so I can trigger a scaling event and observe the system responding.

**Why this priority**: This is the interactive heart of the demonstration. The page still has value with just the initial metrics view (P1), but the ability to initiate a scaling event is the feature's defining interaction.

**Independent Test**: Can be fully tested by entering a valid message count, submitting the request, and confirming the system acknowledges the submission and begins monitoring. No chart history is required — simply confirming submission succeeds is enough.

**Acceptance Scenarios**:

1. **Given** a visitor enters a valid message count and submits the form, **When** the submission is accepted, **Then** the system confirms messages have been queued and transitions the dashboard into monitoring mode.
2. **Given** a visitor enters a message count below the minimum allowed, **When** they attempt to submit, **Then** the input is rejected before sending, and the visitor is informed of the valid range.
3. **Given** a visitor enters a message count above the maximum allowed (5000), **When** they attempt to submit, **Then** the input is rejected before sending, and the visitor is informed of the valid range.
4. **Given** a visitor submits messages and the scaling service returns an error, **When** the submission fails, **Then** a clear error message is displayed and the visitor can attempt again.
5. **Given** a visitor attempts to submit messages while the queue is not yet empty from a previous batch, **When** the scaling service rejects the submission, **Then** the dashboard displays a distinct message explaining that the queue is still active, including the current number of messages still queued, and the visitor is guided to wait before trying again.

---

### User Story 3 - Observe Live Scaling Behaviour (Priority: P3)

As a visitor who has submitted messages, I want to see the queue depth plotted over time and the replica count updating automatically, so I can observe how the container app scales in response to queue pressure.

**Why this priority**: The live chart and polling represent the educational payoff of the demonstration. They depend on a successful message submission (P2) and the initial metrics view (P1), making them P3 but the most compelling part of the feature.

**Independent Test**: Can be fully tested by submitting a valid message count, waiting for at least two polling cycles, and confirming the queue depth chart gains new data points and the replica count panel reflects the latest value.

**Acceptance Scenarios**:

1. **Given** a visitor has submitted messages, **When** monitoring begins, **Then** a time-series chart appears showing queue depth from the moment of submission and updates with each poll.
2. **Given** monitoring is active, **When** each polling interval elapses, **Then** the replica count panel updates to show the most recently retrieved value.
3. **Given** the queue depth returns to zero during monitoring, **When** a poll confirms an empty queue, **Then** monitoring stops automatically and the chart shows the full scaling event from start to finish.
4. **Given** a monitoring session has run for an extended period without the queue emptying, **When** the maximum monitoring duration is reached, **Then** monitoring stops and the visitor is notified that monitoring has ended.
5. **Given** monitoring is active and the scaling service returns an error during a poll, **When** the error is received, **Then** monitoring stops, a user-friendly error message is displayed, and all chart data and metric readings captured up to that point remain visible on screen.
6. **Given** the replica count drops to zero during an active monitoring session, **When** the replica count has not recovered above zero within the configured timeout period, **Then** monitoring stops, a user-friendly error message is shown to the visitor, and all data captured up to that point remains visible on screen.
7. **Given** the replica count drops to zero during an active monitoring session, **When** the replica count recovers above zero before the timeout elapses, **Then** monitoring continues normally without surfacing an error.

---

### Edge Cases

- What happens when the scaling service returns an error partway through an active monitoring session? *(Resolved: monitoring stops, a user-friendly error message is displayed, but all chart data and metric readings captured up to that point remain visible on screen.)*
- How does the dashboard behave if the replica count drops to zero during monitoring? *(Resolved: a configurable timer starts; if the replica count does not recover above zero within that period, monitoring stops and an error is shown to the visitor.)*
- What is displayed on the chart if the queue empties so quickly that only one data point is captured? *(Resolved: all captured data points remain visible on screen regardless of how many were recorded before the queue emptied.)*
- How does the dashboard handle a visitor who navigates away and returns during an active scaling event? *(Resolved: dashboard state resets on navigation; if the queue is still processing, the 429 response on next submission will inform the visitor of the remaining message count.)*
- How should the dashboard behave if a visitor submits messages while a previous request is still being processed? *(Resolved: the scaling service returns a 429 response; the dashboard must present a distinct "request already in progress" message rather than a generic error.)*

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard MUST display the current number of running container instances (replica count) when a visitor first navigates to the page.
- **FR-002**: The dashboard MUST display the current number of messages waiting in the queue (queue depth) when a visitor first navigates to the page.
- **FR-003**: The system MUST retrieve the active container revision identifier on page load in order to provide the replica count.
- **FR-004**: The dashboard MUST provide a clearly labelled numeric input for the visitor to specify how many messages to send.
- **FR-005**: The system MUST enforce a configurable minimum and a maximum of 5000 on the message count input, rejecting out-of-range values before any submission is made.
- **FR-006**: The system MUST provide a clearly labelled action control that submits the specified message count to the scaling service.
- **FR-007**: After a successful message submission, the system MUST begin automatically polling the queue depth and replica count at regular intervals.
- **FR-008**: During an active monitoring session, the dashboard MUST display a time-series chart that plots queue depth against elapsed time, updating with each polling interval.
- **FR-009**: During an active monitoring session, the replica count panel MUST update with the most recently retrieved value after each poll.
- **FR-010**: The system MUST automatically stop polling when the queue depth reaches zero or when the monitoring session exceeds the maximum permitted duration. In both cases, all chart data and metric readings captured up to that point MUST remain visible on screen.
- **FR-011**: The dashboard MUST display a user-friendly error message when the scaling service cannot be reached or returns an unexpected error, both during initial load and during an active monitoring session. When an error occurs mid-session, any chart data and metric readings already captured MUST remain visible on screen.
- **FR-013**: The dashboard MUST distinguish a "queue not empty" rejection from a general service failure, and MUST present a specific message to the visitor that includes the number of messages still in the queue, guiding them to wait until processing completes before retrying.
- **FR-014**: If the replica count drops to zero during an active monitoring session, the system MUST start a configurable timer. If the replica count does not recover above zero before the timer elapses, monitoring MUST stop and a user-friendly error message MUST be displayed, with all previously captured data remaining visible. If the count recovers before the timer elapses, monitoring MUST continue without interruption.
- **FR-012**: The dashboard layout MUST be structured so that additional metric panels or monitoring controls can be added in future iterations without redesigning the existing layout.

### Key Entities *(include if feature involves data)*

- **Scaling Dashboard**: The dedicated page presenting real-time container scaling metrics and the message submission controls.
- **Queue Depth**: The point-in-time count of messages currently waiting in the processing queue; the primary metric driving visible scaling behaviour.
- **Replica Count**: The number of active container instances running at a given moment; the metric that shows the scaling response.
- **Active Revision**: The identifier of the currently deployed container revision, required to query the replica count.
- **Scaling Event**: The period beginning when a visitor submits messages and ending when the queue empties or monitoring times out; the unit of observable activity on the dashboard.
- **Queue Depth Reading**: A single measurement of queue depth captured at a specific point in time during a scaling event, used to build the time-series chart.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The current replica count and queue depth are both visible to a visitor within 5 seconds of navigating to the dashboard page.
- **SC-002**: A visitor can successfully submit a valid message count in under 30 seconds from first viewing the dashboard.
- **SC-003**: After submission, the queue depth chart begins displaying data points within 10 seconds.
- **SC-004**: The replica count panel reflects the latest value within two polling intervals of an actual scaling change occurring.
- **SC-005**: All out-of-range message count inputs are blocked before submission and accompanied by a message indicating the valid range.
- **SC-006**: The dashboard presents an informative, non-broken error state when the scaling service is unreachable, with no raw error details exposed to the visitor.
- **SC-007**: The dashboard page is fully usable and readable on both desktop and common mobile screen sizes.

## Assumptions

- The scaling service API (defined in `specs/openapi-aca-scaling.yaml`) is available and accessible from the personal website's server-side backend.
- The minimum and maximum valid message counts are configurable at deployment time (defaults: minimum 1, maximum 5000). The ACA API hard-caps at 5000 regardless of configuration.
- Polling interval and maximum monitoring duration will be determined during planning; the spec assumes reasonable defaults will be chosen that allow scaling behaviour to become visible without excessive wait times.
- Queue depth readings captured during a scaling event are held in memory for the duration of the page session and are not persisted to a database or retained across page navigations.
- The dashboard is publicly accessible and does not require the visitor to authenticate.
- The existing personal website navigation and visual style (established in `specs/001-personal-website`) will be extended to include the scaling dashboard as an additional page, without changing existing pages.
- Mobile and desktop browser support is required per the site constitution.
- The zero-replica recovery timeout (FR-014) is a configurable value set at deployment time, not adjustable by the visitor. A reasonable default will be determined during planning.
- The scaling service enforces a non-empty-queue constraint server-side: submitting messages while the queue still has active messages returns a 429 response whose body includes the current active message count. The dashboard treats this as a distinct, expected state and surfaces the queue count to the visitor rather than showing a generic error.
