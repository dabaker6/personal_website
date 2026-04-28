# Quickstart: ACA Scaling Dashboard

## Goal

Verify the ACA Scaling Dashboard feature against the existing Flask website, confirming initial load, message submission, live polling, 429 handling, and error states.

## Prerequisites

- Repository dependencies are installed in the local virtual environment.
- `.env` file in the repository root includes `ACA_API_BASE_URL` pointing to a running ACA scaling API instance.
- Optional: set `POLLING_INTERVAL_MS`, `MAX_MONITORING_SECONDS`, and `ZERO_REPLICA_TIMEOUT_SECONDS` to adjust timing for faster local testing.

## Implementation Checklist

1. Create `aca_scaling_api.py` with the API client functions and `AcaScalingApiError` exception.
2. Add `/scaling`, `/scaling/api/status`, and `/scaling/api/send` routes to `app.py`.
3. Add the `Scaling` navigation entry and page content to `content.py`.
4. Create `templates/scaling.html` with metric panels, form, and chart section.
5. Create `static/js/scaling.js` with validation, polling, chart rendering, and timeout logic.
6. Extend `static/css/site.css` with dashboard styles.
7. Add route and API module tests.

## Local Run

```powershell
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000/scaling`.

## Verification Scenarios

### Initial page load

1. Open `/scaling`.
2. Confirm the page returns server-rendered HTML with a visible page title and the two metric panels (queue depth and replica count).
3. Confirm the values shown match the current state of the ACA API (verify against a direct API call if needed).
4. Confirm the `Scaling` navigation link is marked active.
5. Confirm the page is readable on a mobile-width viewport (375px).

### Valid message submission and monitoring

1. Enter a valid message count (e.g., `50`) in the input.
2. Click the send button.
3. Confirm the button is disabled during the request.
4. Confirm a status message appears confirming messages were sent.
5. Confirm the chart section becomes visible.
6. Wait for at least two polling cycles and confirm:
   - The queue depth chart gains new data points.
   - The replica count panel updates.
7. Wait for the queue to empty and confirm:
   - Polling stops automatically.
   - The chart remains visible with all captured data points.
   - No error message appears.

### Input validation

1. Enter `0` and click send — confirm inline error appears before any API call.
2. Enter `5001` and click send — confirm inline error appears.
3. Enter a non-numeric value — confirm the input's `min`/`max` attributes block submission via browser native validation.

### 429 — queue not empty

1. Submit a message batch.
2. While monitoring is active, attempt to submit another message count.
3. Confirm the response shows a message referencing the number of messages still in the queue.
4. Confirm this is visually distinct from a generic error.

### Error mid-session

1. Start monitoring (submit a valid batch).
2. Disable the ACA API or modify `ACA_API_BASE_URL` to point to an unreachable host.
3. Wait for the next poll to fail.
4. Confirm monitoring stops.
5. Confirm an error message is displayed.
6. Confirm all chart data captured before the error remains visible.

### Zero-replica timeout (requires staging control)

1. Submit a message batch.
2. If possible, force the replica count to zero (e.g., by scaling the container app to 0 manually).
3. Confirm a timer begins (no immediate error).
4. If the replica count does not recover within `ZERO_REPLICA_TIMEOUT_SECONDS`, confirm monitoring stops and the timeout error message appears.
5. Confirm all chart data captured before the timeout remains visible.

### ACA API unavailable on page load

1. Set `ACA_API_BASE_URL` to an unreachable host.
2. Open `/scaling`.
3. Confirm the page returns `200 OK` with an error message in place of metric values.
4. Confirm no stack trace or raw error detail is visible.

## Automated Verification

```powershell
.\.venv\Scripts\python.exe -m pytest
```

All new tests should pass. Existing tests should be unaffected.
