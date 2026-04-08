# Feature Specification: Cricket API Integration

**Feature Branch**: `003-cricket-api`  
**Created**: 2026-04-08  
**Status**: Implemented  
**Input**: User description: "I want to create a new feature to add access to a backend api. Branch from main and reference the existing personal website in specs\001-personal-website. Initially users should be able to search for matches using the browse endpoint, then select a match using the matchId endpoint to return a detailed output of the match. All query parameters from the browse endpoint should be available to the user. fromDate and toDate should be a date range picker. Gender should be a dropdown with male/female. Matchtype should be Test, ODI, T20, IT20, ODM or MDM. Venue, eventName and team are free type for now, but should support API-driven options later. The feature should be done in Flask rather than JavaScript and match the current site look and feel." 

**References**: [001-personal-website spec](../001-personal-website/spec.md)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search for Matches (Priority: P1)

As a site visitor, I want to open a matches page and search using all available browse filters, so I can find cricket matches relevant to my criteria.

**Why this priority**: The browse flow is the entry point for the whole feature. Without it, the backend integration provides no user value.

**Independent Test**: Open `/matches`, submit one or more filters, and confirm the page renders matching results from the backend in server-rendered HTML.

**Acceptance Scenarios**:

1. **Given** a visitor opens the matches page, **When** the page loads, **Then** they see a search form that exposes all browse endpoint query parameters.
2. **Given** a visitor wants to filter by date, **When** they interact with the form, **Then** `fromDate` and `toDate` are presented as date inputs that work together as a date range.
3. **Given** a visitor wants to filter by gender or match type, **When** they open the relevant controls, **Then** the allowed values are available as dropdown options.
4. **Given** a visitor submits one or more filters, **When** the backend returns matches, **Then** the page shows a list of result summaries including teams, date, competition, and venue.

---

### User Story 2 - View a Match Summary (Priority: P2)

As a site visitor, I want to select a match from the results list and see a concise summary derived from the match document, so I can inspect the result without reading the full raw JSON payload.

**Why this priority**: Search without a follow-through detail view is incomplete. This story delivers the first usable end-to-end browse-to-detail experience.

**Independent Test**: From `/matches`, select a result and confirm the detail route renders a concise summary using the backend match document's `info` section.

**Acceptance Scenarios**:

1. **Given** search results are displayed, **When** a visitor selects one match, **Then** they are taken to a dedicated detail page for that match.
2. **Given** the detail page loads successfully, **When** the page renders, **Then** it shows a brief summary including event name, match type, gender, teams, venue, date range, and outcome where available.
3. **Given** a visitor wants to continue browsing, **When** they are on the match detail page, **Then** a clear path back to the search results is available.

---

### User Story 3 - Recover Gracefully from Backend Problems (Priority: P3)

As a site visitor, I want the site to fail clearly when the backend API is unavailable or rejects a request, so I understand that the data could not be loaded instead of seeing a broken page.

**Why this priority**: The feature depends on an external backend. Clear degraded behavior is necessary for a reliable public-facing experience.

**Independent Test**: Simulate browse and detail API failures and verify the UI still renders a useful error state instead of crashing or returning incomplete markup.

**Acceptance Scenarios**:

1. **Given** the browse API is unavailable, **When** a visitor submits filters, **Then** the matches page remains usable and displays a clear error message.
2. **Given** the match detail API is unavailable for a selected match, **When** the visitor opens the detail route, **Then** the route returns a rendered error state rather than an unhandled exception.
3. **Given** no matches are returned for the submitted filters, **When** the search completes, **Then** the page shows a clear no-results state.

---

### Edge Cases

- What happens when the visitor opens `/matches` with no filters yet?
- What happens when the backend returns fewer than two teams in a match summary or detail payload?
- How does the UI behave when the backend returns `hasMore: true` but only the first result page is shown?
- What happens when the API returns a detail document with missing or partial `info` fields?
- How does the feature behave when `fromDate` is later than `toDate` and the backend rejects the request?
- What happens when a match ID contains characters that must be URL encoded?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a dedicated Matches page reachable from the site's primary navigation.
- **FR-002**: The Matches page MUST expose all browse endpoint query parameters: `gender`, `fromDate`, `toDate`, `venue`, `matchType`, `eventName`, and `team`.
- **FR-003**: The system MUST render `fromDate` and `toDate` as date inputs suitable for date-range entry.
- **FR-004**: The system MUST render `gender` as a dropdown with `male` and `female` values.
- **FR-005**: The system MUST render `matchType` as a dropdown with `Test`, `ODI`, `T20`, `IT20`, `ODM`, and `MDM` values.
- **FR-006**: The system MUST render `venue`, `eventName`, and `team` as free-text inputs in the initial release.
- **FR-007**: Submitting the Matches form MUST call the backend browse endpoint and render results as server-generated HTML.
- **FR-008**: Each rendered result MUST provide a clear action that opens a dedicated match detail route.
- **FR-009**: The match detail route MUST call the backend match-by-id endpoint and derive a concise summary from the returned document's `info` section.
- **FR-010**: The detail page MUST display available summary fields without requiring the raw JSON document to be shown.
- **FR-011**: The feature MUST preserve the existing site's navigation, layout style, and responsive behavior.
- **FR-012**: The browse and detail flows MUST be implemented in Flask with server-rendered templates rather than a client-side application flow.
- **FR-013**: The browse page MUST display a clear no-results state when the API returns no matches.
- **FR-014**: The browse page MUST display a clear error state when the browse API request fails.
- **FR-015**: The detail page MUST display a clear error state when the match detail request fails.
- **FR-016**: The system SHOULD preserve the active search filters when a visitor navigates from browse results to match detail and back again.
- **FR-017**: The feature SHOULD remain structurally ready for future API-driven option lists for `venue`, `eventName`, and `team`.

### Key Entities

- **Browse Query**: The set of optional filters submitted by the visitor to the browse endpoint, including gender, date range, venue, match type, event name, and team.
- **Match Summary**: A compact representation of one browse result containing match identifier, teams, venue, competition, and date.
- **Match Detail Document**: The full backend response returned for a selected match identifier.
- **Match Info Summary**: A presentation-focused subset of the detail document derived from the `info` section for display on the detail page.
- **Matches Page**: The server-rendered page containing the browse form, result list, no-results state, and browse-level error state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A visitor can submit a browse query from `/matches` and receive a rendered results page in one form submission with no client-side app dependency.
- **SC-002**: 100% of supported browse query parameters are visible in the Matches form.
- **SC-003**: A visitor can navigate from `/matches` to a selected match detail page in one click from the rendered result list.
- **SC-004**: When the backend returns a valid detail document, the detail page presents a concise human-readable summary without exposing raw JSON by default.
- **SC-005**: When the backend API fails for browse or detail requests, the route still returns usable HTML containing a clear error state.
- **SC-006**: The new Matches route remains visually consistent with the rest of the personal website on desktop and mobile layouts.

## Assumptions

- The existing Flask personal website defined in the 001 feature remains the host application for this feature.
- The backend browse and detail endpoints already exist and are reachable through a configurable base URL.
- The first release only requires server-rendered search and summary pages; richer interactions such as autocomplete, pagination controls, and raw document views are out of scope.
- The concise detail view is intentionally limited to fields derived from the backend document's `info` section.
- Future option-list endpoints for `venue`, `eventName`, and `team` may be added later without changing the primary route structure.
