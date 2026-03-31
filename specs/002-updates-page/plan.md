# Implementation Plan: Updates Page

**Branch**: `002-updates-page` | **Date**: 2026-03-31 | **Spec**: `/specs/002-updates-page/spec.md`
**Input**: Feature specification from `/specs/002-updates-page/spec.md`

**Note**: This plan extends the existing Flask personal website from `/specs/001-personal-website/plan.md` and fits the current `app.py`, `content.py`, `templates/`, and `tests/` structure.

## Summary

Add a server-rendered Updates section to the existing Flask site using Markdown files with YAML frontmatter as the source of truth. The feature will introduce a filesystem-backed content loader, a feed route, an entry detail route, two new templates, light client-side filtering and sorting for the feed, and route-level tests. New posts will appear automatically when a Markdown file is added under the updates content directory, with no further code changes.

## Technical Context

**Language/Version**: Python 3.14  
**Primary Dependencies**: Flask, pytest, Python-Markdown, python-frontmatter  
**Storage**: Filesystem-based Markdown content under `content/updates/`  
**Testing**: pytest  
**Target Platform**: Modern desktop and mobile web browsers served by a Python runtime  
**Project Type**: web-service  
**Performance Goals**: Server-rendered feed and detail pages return meaningful HTML on first response; default feed load for 50 entries remains under 2 seconds; client-side search and sort feel effectively immediate for the same dataset  
**Constraints**: Must preserve server-side rendering for primary content; must fit the current single-app Flask layout; no client-side framework; adding a new post must require only a new Markdown file; malformed entries must not break the feed; navigation and styling must remain consistent with the existing site  
**Scale/Scope**: Small public-facing updates system for a personal site with tens of posts, two new routes, a single content directory, and route-level automated verification

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: The Updates feed and entry detail remain server-rendered Flask routes that return usable HTML on first response.
- PASS: The design keeps the current small server-first architecture: one Flask app, Jinja templates, static CSS, and a focused content-loading module rather than a second frontend stack.
- PASS: Interactive search and sorting are progressive enhancement layered on top of a fully usable server-rendered feed.
- PASS: The feature includes a documented verification path and route-level automated checks for the new routes and degraded-content behavior.
- PASS: No secrets or deployment-sensitive configuration are introduced; content is read from repository-managed Markdown files.

Post-design re-check:

- PASS: Phase 1 artifacts keep the implementation within the same Flask SSR structure and do not introduce constitutional exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/002-updates-page/
├── contracts/
│   └── updates-routes.md
├── data-model.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md
```

### Source Code (repository root)

```text
app.py
content.py
updates.py
requirements.txt
README.md
content/
└── updates/
    ├── 2026-03-31-launch-note.md
    └── 2026-04-01-design-log.md
static/
├── css/
│   └── site.css
└── js/
    └── updates.js
templates/
├── about.html
├── base.html
├── contact.html
├── index.html
├── update_detail.html
└── updates.html
tests/
└── test_routes.py
```

**Structure Decision**: Keep the existing single-file Flask application and shared template model from the personal website feature. Add one dedicated `updates.py` content-loader module instead of overloading `content.py` with Markdown parsing logic. This keeps static site metadata centralized in `content.py`, isolates filesystem-backed update parsing, and lets new routes integrate into `app.py` with minimal disruption.

## Complexity Tracking

No constitutional violations or complexity exceptions were identified. The selected approach adds one focused content-loading module and a small progressive-enhancement script, which is the simplest way to satisfy automatic post discovery, search, and sorting without introducing a second application layer.
