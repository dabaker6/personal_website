# Route Contracts: ACA Scaling Dashboard

## GET /scaling

### Purpose

Render the ACA Scaling Dashboard as a server-rendered HTML page showing current queue depth, replica count, and the message submission form.

### Inputs

None required.

### Response Contract

- Returns `200 OK` in all cases (both success and ACA API error paths).
- Returns a complete HTML document through the shared site layout (`base.html`).
- On success, includes:
  - Current queue depth displayed in a labelled metric panel.
  - Current replica count displayed in a labelled metric panel.
  - A message submission form with a number input bounded by `min_messages` and `max_messages`.
  - A dashboard container element with `data-*` attributes carrying all config values:
    - `data-polling-interval-ms`
    - `data-max-monitoring-seconds`
    - `data-zero-replica-timeout-seconds`
    - `data-min-messages`
    - `data-max-messages`
  - Target elements for JS updates: `data-replica-count`, `data-queue-depth`, `data-chart-section`, `data-status-message`.
- On ACA API failure, includes:
  - An informative error message in place of metric values.
  - The submission form remains absent or disabled (no valid initial revision name).
  - No raw error details or stack traces exposed.

### Navigation

- The `Scaling` navigation link is marked active (`is-active`) when this page is rendered.

---

## GET /scaling/api/status

### Purpose

Return the current scaling state as JSON for client-side polling during a monitoring session.

### Inputs

None required.

### Success Response — 200

```json
{
  "queue_length": 42,
  "replica_count": 3,
  "revision_name": "my-app--revision-abc123"
}
```

- `queue_length`: Non-negative integer.
- `replica_count`: Non-negative integer.
- `revision_name`: Non-empty string.

### Error Response — 500

```json
{
  "error": "Human-readable description of the failure.",
  "code": "InternalServerError"
}
```

- Returned when any ACA API call fails.
- No HTML content is returned for this endpoint under any condition.

---

## POST /scaling/api/send

### Purpose

Proxy a message-send request to the ACA scaling API after server-side input validation.

### Inputs

JSON body:

```json
{ "count": 100 }
```

- `count`: Integer. Must satisfy `1 ≤ count ≤ 5000`.

### Success Response — 202

```json
{ "message_count": 100 }
```

### Error Responses

**400 — Out-of-range input** (rejected before calling ACA API):

```json
{ "error": "Message count must be between 1 and 5000." }
```

**429 — Queue not empty** (ACA API returned 429):

```json
{
  "error": "Queue is not empty. A previous batch is still being processed.",
  "queue_length": 42
}
```

- `queue_length` is the active message count parsed from the ACA API 429 response body.
- If the count cannot be parsed, `queue_length` is `null`.

**500 — ACA API failure**:

```json
{ "error": "Human-readable description of the failure." }
```

### Shared Contract

- All responses use `Content-Type: application/json`.
- No HTML is returned by this endpoint.
- Server-side validation (400) fires before any ACA API call is made.
