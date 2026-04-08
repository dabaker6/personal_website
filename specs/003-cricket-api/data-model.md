# Data Model: Cricket API Integration

## Browse Query

Represents the set of optional search filters submitted from the Matches page.

### Fields

- `gender`: Optional string value, currently `male` or `female` when selected.
- `fromDate`: Optional ISO-format date string.
- `toDate`: Optional ISO-format date string.
- `venue`: Optional free-text search term.
- `matchType`: Optional string value from the approved match-type set.
- `eventName`: Optional free-text search term.
- `team`: Optional free-text search term.

### Validation Rules

- All fields are optional.
- Empty values are omitted from outbound browse requests.
- `gender` is constrained by the rendered UI to `male` or `female`.
- `matchType` is constrained by the rendered UI to `Test`, `ODI`, `T20`, `IT20`, `ODM`, or `MDM`.
- Date ordering may still be validated by the backend even if both values are syntactically valid.

## Match Summary

Represents one item returned from the browse endpoint.

### Fields

- `match_id`: Backend identifier used to request detail data.
- `teams`: Ordered list of team names.
- `venue`: Venue string.
- `competition`: Competition or event label from the browse response.
- `date`: Primary date label from the browse response.

### Validation Rules

- `match_id` is required for actionable results.
- `teams` may contain fewer than two values in degraded data but the UI should still remain renderable.
- The route should tolerate missing display fields by rendering partial summaries rather than failing.

## Match Detail Document

Represents the raw backend payload returned by the match-by-id endpoint.

### Fields

- `matchId`: Echo of the selected backend identifier.
- `document`: Arbitrary match document payload as returned by the backend.

### Validation Rules

- `document` is treated as backend-owned JSON.
- The first release reads only the subset required to build an info summary.

## Match Info Summary

Represents the curated detail view model derived from `document.info`.

### Fields

- `match_id`: Selected backend identifier.
- `event_name`: Event or series name.
- `match_type`: Match type label.
- `gender`: Gender label.
- `venue`: Venue name.
- `city`: City label if present.
- `team_a`: First team name if available.
- `team_b`: Second team name if available.
- `start_date`: First date in the document's date list.
- `end_date`: Last date in the document's date list.
- `outcome`: Concise presentation string assembled from result and winner fields when available.

### Validation Rules

- Any field may be empty if the backend document omits it.
- The summary model must remain renderable even when some `info` fields are absent.
- Date display can be derived from one date or a start/end date pair.

## Matches Page View Model

Represents the server-rendered state for `/matches`.

### Fields

- `query`: Current `Browse Query` values.
- `matches`: Zero or more `Match Summary` items.
- `has_more`: Boolean indicating more results exist upstream.
- `total_matched`: Optional numeric count returned by the backend.
- `error_message`: Optional browse-level error message.

### Validation Rules

- `matches` may be empty because no search has been run yet or because no matches were returned.
- `error_message` and populated result content should not both represent the primary state for the same request.

## Match Detail Page View Model

Represents the server-rendered state for `/matches/<match_id>`.

### Fields

- `match_id`: Requested backend identifier.
- `summary`: Optional `Match Info Summary`.
- `error_message`: Optional detail-level error message.
- `back_url`: Route back to the browse page, optionally preserving filters.

### Validation Rules

- `summary` is present for successful detail requests.
- `error_message` is present for failed detail requests.
- `back_url` should preserve active browse filters when they were supplied.
