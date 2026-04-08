# Route Contracts: Cricket API Integration

## GET /matches

### Purpose

Render the public matches browse page as server-rendered HTML.

### Inputs

Optional query parameters:

- `gender`
- `fromDate`
- `toDate`
- `venue`
- `matchType`
- `eventName`
- `team`

### Response Contract

- Returns `200 OK` when the route is available.
- Returns a complete HTML document through the shared site layout.
- Includes the Matches page heading and introductory copy.
- Includes a browse form exposing all supported query parameters.
- When at least one filter is submitted and the backend returns results, includes zero or more result cards exposing:
  - teams
  - date
  - competition
  - venue
  - link to the selected match detail route
- When a search returns no results, includes a clear no-results state.
- When the backend browse request fails, includes a clear browse-level error state.

### Failure Behavior

- Upstream API failure does not prevent the route from returning HTML.
- Invalid or rejected query combinations may surface as a rendered error state supplied by the backend integration layer.
- The route remains usable with no submitted filters.

## GET /matches/<match_id>

### Purpose

Render a concise summary for one selected match as server-rendered HTML.

### Inputs

- `match_id`: Path parameter identifying the selected backend match.
- Optional browse query parameters may also be present to preserve the route back to search results.

### Response Contract

- Returns `200 OK` when the backend detail request succeeds.
- Returns a complete HTML document through the shared site layout.
- Includes a concise summary derived from the backend document `info` section, including available event, match type, gender, teams, venue, date, and outcome information.
- Includes a route back to `/matches`, preserving filters when supplied.

### Error Contract

- Returns `502 Bad Gateway` when the upstream detail request fails but the site can still render a useful error page.
- Returns a complete HTML document containing the shared navigation and a clear detail-level error state.

## Shared Rendering Contract

- Both routes inherit the existing shared layout from `templates/base.html`.
- Both routes remain usable with JavaScript disabled.
- The browse and detail flow is driven by Flask route handling and standard links/forms rather than client-side application state.
