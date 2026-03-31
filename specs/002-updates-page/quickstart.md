# Quickstart: Updates Page

## Goal

Verify the updates feature against the existing Flask website structure using Markdown files as the source of truth.

## Prerequisites

- The repository dependencies are installed in the local virtual environment.
- Additional Markdown/frontmatter dependencies from the implementation plan are installed.

## Implementation Checklist

1. Add the planned dependencies to `requirements.txt`.
2. Create the `content/updates/` directory and add at least two sample Markdown entries with valid frontmatter.
3. Add a dedicated loader module for reading, validating, and formatting update entries.
4. Add a feed route and detail route to `app.py`.
5. Add `Updates` to the shared navigation data in `content.py`.
6. Create `templates/updates.html` and `templates/update_detail.html`.
7. Add progressive-enhancement JavaScript for search, tag filtering, and sort.
8. Extend `static/css/site.css` for the feed, detail view, empty states, and filter controls.
9. Add route-level tests for the feed, detail pages, draft exclusion, malformed-entry resilience, and navigation.

## Local Run

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000/updates`.

## Verification Scenarios

### Feed rendering

1. Open `/updates`.
2. Confirm the page returns HTML with a visible title, timestamps, tags, and summaries.
3. Confirm the entries appear newest first.
4. Confirm the primary navigation includes `Updates`.

### Detail rendering

1. Open one update entry from the feed.
2. Confirm the detail page renders the entry title, timestamp, tags, and Markdown body.
3. Confirm a clear route back to the feed exists.

### Progressive enhancement

1. Type a known term into the search field.
2. Confirm the visible results update without a page reload.
3. Click a tag.
4. Confirm the feed filters to matching entries.
5. Change the sort control.
6. Confirm the visible entries reorder without a page reload.

### Content workflow

1. Add a new Markdown file to `content/updates/` with valid `title` and `date` frontmatter.
2. Reload `/updates`.
3. Confirm the new entry appears with no code changes.
4. Add `draft: true` to an entry and confirm it disappears from public output.
5. Add a malformed entry and confirm the rest of the feed still renders.

## Automated Verification

```powershell
.\.venv\Scripts\python.exe -m pytest
```
