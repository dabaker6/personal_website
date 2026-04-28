# Data Model: ACA Scaling Dashboard

## AcaScalingApiError

Exception raised by `aca_scaling_api.py` when the upstream ACA API returns an unexpected or error response.

### Fields

- `message`: Human-readable error description string.
- `status_code`: HTTP status code returned by the ACA API, or `None` for connection-level failures.
- `active_message_count`: Integer count of active messages remaining in the queue, populated only when `status_code` is `429`; `None` otherwise.

### Validation Rules

- `active_message_count` must be parsed from the `message` field of the 429 response body (`"Queue is not empty. Current active message count: N."`).
- If parsing fails, `active_message_count` defaults to `None` and the error is still raised.

---

## ScalingStatus

Represents a single point-in-time snapshot of the ACA scaling state, returned by `get_revision_name()`, `get_replica_count()`, and `get_queue_length()` and assembled in the `/scaling/api/status` endpoint.

### Fields

- `revision_name`: String identifier of the currently active Container App revision.
- `replica_count`: Non-negative integer count of running container instances at the time of query.
- `queue_length`: Non-negative integer count of active (non-dead-lettered) messages in the Service Bus queue at the time of query.

### Validation Rules

- `replica_count` and `queue_length` must be non-negative integers.
- `revision_name` must be a non-empty string matching `^[a-zA-Z0-9-]+$` (enforced by the ACA API).

---

## ScalingConfig

Configuration values controlling dashboard polling and timeout behaviour. Read from environment variables in `app.py` and embedded in the template as `data-*` attributes for consumption by `scaling.js`.

### Fields

- `polling_interval_ms`: Milliseconds between each status poll during an active monitoring session. Default: `5000`.
- `max_monitoring_seconds`: Maximum total duration of a monitoring session in seconds. Default: `300`.
- `zero_replica_timeout_seconds`: Seconds to wait for replica count to recover above zero before stopping monitoring with an error. Default: `60`.
- `min_messages`: Minimum valid message count for submission. Fixed: `1`.
- `max_messages`: Maximum valid message count for submission. Fixed: `5000` (matches ACA API constraint).

### Validation Rules

- All values must be positive integers.
- `min_messages` and `max_messages` are constants and not overridden by environment variables.

---

## QueueDepthReading

An in-memory data point captured by `scaling.js` during an active monitoring session. Not persisted; exists only for the duration of the page session.

### Fields

- `elapsed_ms`: Number of milliseconds elapsed since monitoring started when this reading was captured.
- `queue_length`: Integer queue depth at the time of this reading.

### Derived Behaviours

- Readings are accumulated in a JS array throughout the monitoring session.
- The array is used as the data source for the SVG time-series chart.
- The array is preserved (not cleared) when monitoring stops, regardless of the stop condition.
- The array is discarded when the user navigates away from the page.

---

## NavigationItem (scaling)

Represents the new top-level navigation entry for the Scaling Dashboard page.

### Fields

- `label`: `"Scaling"`
- `endpoint`: `"scaling"` — Flask endpoint name for `url_for()` resolution.
- `slug`: `"scaling"` — used by `base.html` to mark the active navigation link.

### Validation Rules

- Must be added to the `navigation` list in `content.py` without modifying existing entries.
- Must be reachable from any primary page in one interaction.

---

## Relationships

- One `/scaling` route assembles one `ScalingStatus` from three ACA API calls and passes it alongside one `ScalingConfig` to the template.
- One `/scaling/api/status` call produces one fresh `ScalingStatus` snapshot returned as JSON.
- One monitoring session accumulates many `QueueDepthReading` records, each appended after a successful `/scaling/api/status` poll.
- One `QueueDepthReading` array drives one SVG time-series chart for the lifetime of the session.
