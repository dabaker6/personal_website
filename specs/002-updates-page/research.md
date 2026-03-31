# Research: Updates Page

## Decision 1: Store updates as Markdown files in a dedicated `content/updates/` directory

- Decision: Keep each published update as an individual Markdown file under `content/updates/`, with the filename serving as the basis for the entry slug.
- Rationale: This satisfies the requirement that new posts appear without application code changes, keeps authoring lightweight for a personal site, and matches the existing repository’s file-based content model.
- Alternatives considered:
  - Extend `content.py` with inline post content: rejected because every new post would require a code edit.
  - Use a database-backed model: rejected because it adds operational complexity and configuration that the feature does not need.
  - Use a single aggregate JSON/YAML file: rejected because it makes each new post an edit to a central registry rather than an additive content file.

## Decision 2: Use `python-frontmatter` for metadata parsing and `Python-Markdown` for body rendering

- Decision: Parse frontmatter with `python-frontmatter` and render Markdown with `Python-Markdown`.
- Rationale: These libraries keep the implementation small and readable while covering the exact needs of frontmatter-driven content and safe server-side Markdown rendering.
- Alternatives considered:
  - Manual frontmatter parsing: rejected because it is brittle and duplicates well-understood parsing behavior.
  - `markdown2`: rejected because `Python-Markdown` is more widely used and keeps extensions explicit.
  - `mistune`: rejected because it would also work, but the feature does not need its extra flexibility.

## Decision 3: Load entries through a dedicated `updates.py` module

- Decision: Introduce `updates.py` as a focused content-loading module responsible for scanning the content directory, validating frontmatter, normalizing slugs and dates, excluding drafts, and returning feed/detail-ready data structures.
- Rationale: The existing `content.py` file is currently a static configuration source for site-wide copy and navigation. Separating Markdown entry handling avoids mixing two different content concerns in one file and keeps route logic in `app.py` thin.
- Alternatives considered:
  - Add all Markdown logic to `content.py`: rejected because it grows a static content module into a mixed configuration and parsing layer.
  - Parse files directly inside route functions: rejected because it makes the route handlers harder to test and reuse.

## Decision 4: Use progressive enhancement for search, tag filtering, and sort

- Decision: Render the full feed on the server, then use a small vanilla JavaScript file to filter and sort already-rendered entry metadata in the browser.
- Rationale: This preserves server-side rendering as the core delivery model while satisfying the no-reload interaction requirement. It also avoids adding a client-side framework to a small Flask site.
- Alternatives considered:
  - Server-driven search and sort via query parameters: rejected because the spec explicitly calls for no-reload interactions.
  - A client-side framework or SPA widget: rejected because it violates the constitution’s simplicity bar for this scope.

## Decision 5: Skip malformed entries rather than failing the whole page

- Decision: If an entry has malformed frontmatter, an invalid date, or unreadable body content, exclude it from the published feed and continue rendering the remaining entries.
- Rationale: This directly satisfies the requirement that malformed content must not break the feed and keeps the public page resilient.
- Alternatives considered:
  - Hard-fail the route: rejected because one bad post would take down the updates experience.
  - Render malformed entries with placeholder metadata: rejected because invalid dates and missing core identifiers make ordering and linking unreliable.

## Decision 6: Expose public HTML route contracts rather than an API contract

- Decision: Document `GET /updates` and `GET /updates/<slug>` as public HTML route contracts in markdown under `contracts/`.
- Rationale: The project is a server-rendered web app without a JSON API for this feature, so route behavior is the relevant contract.
- Alternatives considered:
  - OpenAPI schema: rejected because there is no feature API.
  - No contract artifact: rejected because the planning workflow expects concrete interface documentation.
