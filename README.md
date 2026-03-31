# Personal Website

This repository contains a small server-rendered Flask personal website with three primary pages: landing, about, and contact.

## Stack

- Flask for server-side rendering
- Jinja templates for shared layout and page rendering
- Centralized content in `content.py`
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

## Verification checklist

- Confirm `/`, `/about`, and `/contact` render meaningful HTML on first response.
- Check desktop and mobile layouts.
- Confirm navigation works without client-side routing.
- Confirm the contact page still renders an acceptable fallback when no public methods are configured.