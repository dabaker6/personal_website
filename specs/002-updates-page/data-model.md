# Data Model: Updates Page

## Update Entry

Represents one published or draft update sourced from a single Markdown file in `content/updates/`.

### Fields

- `slug`: URL-safe identifier derived from the filename without the `.md` suffix.
- `title`: Human-readable entry title from frontmatter.
- `published_at`: Canonical parsed publication date/time derived from the frontmatter `date` field.
- `published_label`: Human-readable formatted date string shown in templates.
- `tags`: Ordered list of keyword tags from frontmatter.
- `summary`: Short summary text from frontmatter, optional.
- `body_markdown`: Raw Markdown body content.
- `body_html`: Server-rendered HTML representation of the Markdown body.
- `body_text`: Plain-text version used for client-side searching.
- `draft`: Boolean flag indicating whether the entry should be excluded from public output.
- `source_path`: Absolute or repository-relative filesystem path to the source Markdown file.

### Validation Rules

- `slug` must be unique across all files in `content/updates/`.
- `title` is required for published output.
- `published_at` is required for published output and must be parseable from the frontmatter `date` field.
- `tags` defaults to an empty list when omitted.
- `summary` defaults to an empty string when omitted.
- `draft` defaults to `false` when omitted.
- Files missing `title` or `date`, or containing invalid frontmatter, are excluded from the public feed.

### Derived Behaviors

- Feed ordering is based on `published_at`, newest first by default.
- Detail route lookup is based on `slug`.
- Client-side search evaluates `title`, `summary`, and `body_text`.
- Tag filtering matches normalized tag values while preserving the original display text.

## Updates Feed View Model

Represents the server-rendered collection of entries shown on `/updates`.

### Fields

- `entries`: List of published `Update Entry` items.
- `available_tags`: Distinct tag values derived from `entries`, sorted for display.
- `default_sort`: Default sort mode presented to visitors, initially `newest`.
- `empty_state_title`: Message shown when there are no entries at all.
- `empty_filter_title`: Message shown when search or tag filtering produces no results.

### Validation Rules

- `entries` may be empty.
- `available_tags` must only include tags from published entries.
- The feed must remain renderable even when one or more source files are invalid.

## Navigation Item

Represents the new top-level site navigation entry for Updates.

### Fields

- `label`: Display label, `Updates`.
- `endpoint`: Flask endpoint name for the feed route.
- `slug`: Navigation identifier used to mark the active page.

### Validation Rules

- Must be added without changing the structure of existing navigation items.
- Must be reachable from any primary page in one interaction.

## Relationships

- One `Updates Feed View Model` contains many `Update Entry` records.
- One `Update Entry` may expose many `Tag` values.
- One `Navigation Item` points to the feed route, while each `Update Entry` points to a detail route derived from its slug.
