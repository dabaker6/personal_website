# Quickstart: Cricket API Integration

## Goal

Verify the server-rendered cricket matches feature against the current Flask personal website and the backend browse/detail API.

## Prerequisites

- The repository dependencies are installed in the local virtual environment.
- The backend cricket API is running and reachable.
- `MATCHES_API_BASE_URL` is set to the backend API root, for example `https://localhost:7019/api/v1`.

## Implementation Checklist

1. Add a dedicated backend integration module for browse and match-by-id requests.
2. Add `/matches` and `/matches/<match_id>` routes to `app.py`.
3. Add `Matches` to the shared navigation in `content.py`.
4. Create `templates/matches.html` with all browse filters rendered in Flask.
5. Create `templates/match_detail.html` for the concise match summary.
6. Extend `static/css/site.css` with matches-specific form and summary styles.
7. Add route tests for form rendering, browse results, detail summaries, and upstream failures.
8. Document environment configuration for the upstream API base URL.

## Local Run

```powershell
$env:MATCHES_API_BASE_URL = "https://localhost:7019/api/v1"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000/matches`.

## Verification Scenarios

### Browse flow

1. Open `/matches`.
2. Confirm the form shows `gender`, `fromDate`, `toDate`, `venue`, `matchType`, `eventName`, and `team`.
3. Confirm `gender` and `matchType` are dropdowns.
4. Confirm `fromDate` and `toDate` are date inputs.
5. Submit one or more filters.
6. Confirm matching results render as HTML cards with date, teams, competition, and venue.

### Detail flow

1. From the results page, select one match.
2. Confirm the detail page renders a concise summary derived from the match document `info` section.
3. Confirm the page shows a route back to the browse results.

### Failure handling

1. Stop or misconfigure the backend API.
2. Submit the browse form.
3. Confirm `/matches` still renders and shows a clear error state.
4. Attempt to open a match detail route.
5. Confirm the detail page returns a rendered error state instead of an unhandled exception page.

## Automated Verification

```powershell
.\.venv\Scripts\python.exe -m pytest
```
