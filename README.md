# Personal Website

This repository contains a small server-rendered Flask personal website with three primary pages: landing, about, and contact.
It also includes an API-backed matches browser at `/matches`.

## Stack

- Flask for server-side rendering
- Jinja templates for shared layout and page rendering
- Centralized content in `content.py`
- Markdown files in `content/updates/` for blog-style update entries
- `python-frontmatter` for YAML frontmatter parsing
- `Markdown` for server-side Markdown-to-HTML rendering
- `pytest` for route-level verification

## Run locally

1. Create or activate a virtual environment.
2. Install dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Start the app:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

4. Open `http://127.0.0.1:5000`.

### Configure matches API endpoint

The matches feature calls an upstream backend API. Set `MATCHES_API_BASE_URL` before starting Flask.

```powershell
$env:MATCHES_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
```

You can also tune request timeout behavior (default: 10 seconds):

```powershell
$env:MATCHES_API_TIMEOUT_SECONDS = "15"
```

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Content model

The first release keeps page copy and public contact details in `content.py`. This keeps the templates focused on presentation and makes later content edits or route additions simpler.

## Add a new page

1. Add a page entry in `content.py` under `pages`.
2. Add a navigation item in `content.py` if the page should appear in the primary nav.
3. Create a matching template in `templates/`.
4. Add a Flask route in `app.py` that renders the new page.
5. Add or update route tests in `tests/test_routes.py`.

## Add a new update entry

No application code changes are required. Create a Markdown file in `content/updates/` with a YAML frontmatter block at the top:

```markdown
---
title: My update title
date: 2026-04-01
tags:
  - release
  - design
summary: A short description shown in the feed.
---

Full Markdown body goes here.
```

Required frontmatter fields: `title`, `date` (ISO 8601 format).
Optional fields: `tags` (list, defaults to empty), `summary` (defaults to empty), `draft` (boolean, defaults to `false`).

Set `draft: true` to keep an entry off the public feed. The filename (without `.md`) becomes the entry's URL slug, e.g. `content/updates/2026-04-01-my-note.md` is served at `/updates/2026-04-01-my-note`.

## Verification checklist

- Confirm `/`, `/about`, and `/contact` render meaningful HTML on first response.
- Check desktop and mobile layouts.
- Confirm navigation works without client-side routing.
- Confirm the contact page still renders an acceptable fallback when no public methods are configured.
- Confirm `/updates` renders the feed with titles, dates, tags, and summaries; entries newest-first.
- Confirm `/updates/<slug>` renders the full Markdown body, entry metadata, and a back-to-feed link.
- Confirm the Updates link is present in the primary navigation on all pages.
- Confirm that dropping a new `.md` file into `content/updates/` causes it to appear on the next page load with no code changes.
- Confirm that an entry with `draft: true` is excluded from the feed and its detail URL returns 404.
- Confirm that a malformed entry file does not break the feed; remaining entries still render.