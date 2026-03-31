# Route Contracts: Updates Page

## GET /updates

### Purpose

Render the public Updates feed as server-rendered HTML.

### Inputs

- No required request parameters.
- Optional non-contractual query parameters may be used later for deep-linking a tag filter, but client-side filtering remains the primary interaction model.

### Response Contract

- Returns `200 OK` when the route is available.
- Returns a complete HTML document through the shared site layout.
- Includes the Updates page heading and introductory copy.
- Includes zero or more published entries, each exposing:
  - title
  - link to detail route
  - visible publication timestamp
  - tag labels
  - summary or excerpt text
- Includes a search control, tag-filter affordance, and sort control.
- Includes an empty state when no published entries exist or when client-side filtering produces no visible matches.

### Failure Behavior

- Malformed content files do not change the route status code.
- Invalid or draft entries are omitted from the rendered feed.
- If no valid published entries exist, the route still returns `200 OK` with an empty-state message.

## GET /updates/<slug>

### Purpose

Render a single published update entry as server-rendered HTML.

### Inputs

- `slug`: Path segment derived from the source Markdown filename.

### Response Contract

- Returns `200 OK` for a published entry with a matching slug.
- Returns a complete HTML document through the shared site layout.
- Includes the entry title, visible publication timestamp, tags, rendered Markdown body, and a route back to the feed.

### Error Contract

- Returns `404 Not Found` when the slug does not match any published entry.
- Returns `404 Not Found` when the matching entry is marked as draft.
- Returns `404 Not Found` when the matching file is malformed and excluded from the published dataset.

## Shared Rendering Contract

- Both routes inherit the existing shared navigation and footer from `templates/base.html`.
- Both routes must remain usable with JavaScript disabled.
- Search, tag filtering, and sorting are enhancements applied after the initial HTML response and must not be required to read entries.
