# Research: ACA Scaling Dashboard

## Decision 1: Use stdlib urllib for ACA API calls — no new HTTP dependency

- **Decision**: Use Python's `urllib.request` and `urllib.error` for all outbound HTTP calls to the ACA scaling API, following the exact pattern already in `matches_api.py`.
- **Rationale**: `matches_api.py` already makes external API calls using `urllib` with no third-party HTTP library. Matching this pattern keeps the dependency set stable (no new entry in `requirements.txt`), keeps the code readable for anyone already familiar with the existing module, and avoids any version-pinning decisions.
- **Alternatives considered**:
  - `requests`: well-known and ergonomic, but introduces a new dependency for functionality already covered by the stdlib.
  - `httpx`: modern async-capable client, but the Flask app is synchronous and the extra capability is unused.

## Decision 2: Flask proxy endpoints for client-side polling

- **Decision**: Add two Flask JSON endpoints — `GET /scaling/api/status` and `POST /scaling/api/send` — so that the client-side JS polls the Flask server rather than calling the ACA API directly.
- **Rationale**: The ACA API URL and any future credentials must not be exposed to the browser. A server-side proxy also lets the Flask layer normalize error formats, validate the message count before it reaches the ACA API, and return consistent JSON regardless of the upstream response shape. This fits the constitution's server-first principle without requiring a separate API service.
- **Alternatives considered**:
  - Direct browser-to-ACA API calls: rejected because it exposes the upstream API base URL and prevents server-side input validation.
  - WebSocket-based push: rejected because the polling interval is coarse (seconds), the feature is a public demonstration with no authenticated users, and the existing codebase has no WebSocket infrastructure.

## Decision 3: Server-rendered initial metrics with JS progressive enhancement

- **Decision**: The `/scaling` route fetches the current revision name, replica count, and queue depth from the ACA API on the server side, embeds the values in the rendered HTML, and then uses vanilla JS for subsequent polling and chart updates.
- **Rationale**: The constitution requires the primary page to return usable server-rendered HTML on first load. Embedding initial metrics in the HTML means visitors see current values even before any JavaScript executes, and the page degrades gracefully if the JS polling fails.
- **Alternatives considered**:
  - Render empty placeholders and fetch all data via JS on load: rejected because it violates the constitution's requirement that the first server response includes meaningful content.
  - Server-sent events (SSE): rejected because it requires a persistent connection and the existing app has no streaming infrastructure; polling at a configurable interval is sufficient for the demonstration.

## Decision 4: Configurable timing values via environment variables and template data attributes

- **Decision**: `polling_interval_ms`, `max_monitoring_seconds`, and `zero_replica_timeout_seconds` are read from environment variables in `app.py` (with documented defaults), then embedded as `data-*` attributes on the dashboard container element. The JS module reads these values from the DOM on initialisation.
- **Rationale**: Environment variables follow the existing dotenv pattern (`python-dotenv` already in `requirements.txt`). Passing values through data attributes avoids inlining Python-specific config into JavaScript and keeps the JS module testable with different config by simply changing the DOM before running tests. This also means no config file format decision is needed.
- **Alternatives considered**:
  - Hard-coded constants in JS: rejected because the spec explicitly requires configurability.
  - A separate `/scaling/api/config` JSON endpoint: rejected because it adds a round-trip before the page is interactive and the values are static for the lifetime of the server process.
  - Jinja variable injection into `<script>` block: rejected because it mixes template and JS scopes in a way that makes the JS harder to test independently.

## Decision 5: Inline SVG time-series chart rendered by vanilla JS

- **Decision**: Render the queue depth chart as an inline SVG string built by JS template literals, inserted via `innerHTML` on the chart host element, following the same approach used in `static/js/match_detail.js`.
- **Rationale**: `match_detail.js` already uses this pattern for the innings progression chart and it has been proven to work within the project's "no build tooling, no chart library" constraint. Reusing the approach keeps the JS consistent and avoids introducing a charting library dependency.
- **Alternatives considered**:
  - Canvas-based rendering: rejected because SVG is already the established pattern in the codebase and is more accessible (screen readers can see SVG text elements).
  - A charting library (Chart.js, Recharts, etc.): rejected because it would require a CDN link or bundling step and introduces an external dependency for functionality the existing SVG pattern can cover.

## Decision 6: 429 active message count parsed from response body message field

- **Decision**: When the ACA API returns 429, `aca_scaling_api.py` parses the active message count from the `message` field of the JSON response body (format: `"Queue is not empty. Current active message count: N."`) and stores it as `AcaScalingApiError.active_message_count`.
- **Rationale**: The ACA API spec defines the 429 response body as an `ApiError` schema where the `message` field carries the count in a predictable string format. Parsing it in the API module keeps the parsing logic in one place and gives the Flask proxy endpoint a clean integer to return to the browser.
- **Alternatives considered**:
  - Return the raw message string to the browser and parse it in JS: rejected because it leaks the internal format into the client and makes the JS fragile if the message format changes.
  - Add a separate `active_count` field to the `ApiError` schema: this would require a spec change to the ACA API; the current approach works with the existing schema.
