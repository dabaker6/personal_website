# Research: Cricket API Integration

## Decision 1: Keep the browse and detail flow fully server-rendered in Flask

- Decision: Implement `/matches` and `/matches/<match_id>` as Flask routes with Jinja templates and standard form submissions.
- Rationale: The user explicitly wanted the feature in Flask rather than JavaScript, and the existing site is already built around server-rendered pages.
- Alternatives considered:
  - Client-side search application: rejected because it would duplicate application flow already handled cleanly by Flask.
  - Hybrid JavaScript-driven API calls: rejected because it would move core behavior out of the existing architecture without a clear need.

## Decision 2: Introduce a dedicated `matches_api.py` integration module

- Decision: Isolate browse-query parsing, upstream HTTP requests, response normalization, and concise summary construction in `matches_api.py`.
- Rationale: This keeps route functions small and testable while avoiding unrelated API concerns leaking into `app.py`.
- Alternatives considered:
  - Inline HTTP logic inside route functions: rejected because it would make route handlers harder to read and harder to test.
  - Extend `content.py` with API integration: rejected because `content.py` is a site metadata/content module, not an integration layer.

## Decision 3: Use the Python standard library for upstream HTTP GET requests

- Decision: Use `urllib.request` and `json` for calling the browse and detail endpoints.
- Rationale: The required integration is simple, read-only, and synchronous. The standard library avoids expanding dependencies just to perform basic GET requests.
- Alternatives considered:
  - `requests`: rejected because it would work well but is unnecessary for the narrow scope of this feature.
  - Async HTTP client: rejected because the rest of the Flask app is synchronous and the scale does not justify added complexity.

## Decision 4: Present a concise detail summary derived from `document.info`

- Decision: The detail page will extract a curated subset of fields from the backend detail payload rather than render raw JSON.
- Rationale: The user asked for a brief summary initially, and the sample document shows the `info` section contains the most useful high-level data for a first release.
- Alternatives considered:
  - Render the full document: rejected because it exposes too much raw structure for the initial user experience.
  - Persist transformed summaries locally: rejected because there is no need for local storage in a request-time integration.

## Decision 5: Keep `venue`, `eventName`, and `team` as free-text fields for now

- Decision: Render these filters as text inputs while keeping the route and template structure ready for later API-driven option lists.
- Rationale: This satisfies the immediate requirement without blocking on additional backend discovery endpoints.
- Alternatives considered:
  - Static option lists: rejected because the set of values is backend-owned and likely large or changeable.
  - Autocomplete in the first release: rejected because no option-list endpoint was yet part of the approved scope.

## Decision 6: Show explicit degraded UI states for upstream failures

- Decision: Map backend failures into clear, rendered error states on both browse and detail pages.
- Rationale: The feature depends entirely on a backend service, so failure behavior must be legible to users and safe for the site.
- Alternatives considered:
  - Bubble exceptions to Flask error pages: rejected because it produces a poor public-facing experience.
  - Silence failures and show empty states only: rejected because it hides the difference between no results and API failure.
