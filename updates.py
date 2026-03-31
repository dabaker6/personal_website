from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass
from datetime import date, datetime

import frontmatter
import markdown as _md

_CONTENT_DIR = pathlib.Path(__file__).parent / "content" / "updates"

_STRIP_TAGS = re.compile(r"<[^>]+>")


@dataclass
class UpdateEntry:
    slug: str
    title: str
    published_at: date
    published_label: str
    tags: list[str]
    summary: str
    body_markdown: str
    body_html: str
    body_text: str
    draft: bool
    source_path: pathlib.Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_slug(path: pathlib.Path) -> str:
    """Return the URL slug for an entry by stripping the .md extension."""
    return path.stem


def _normalize_date(raw: object) -> date:
    """Coerce a raw frontmatter date value to a Python date object.

    python-frontmatter / PyYAML already parses ISO 8601 date scalars as
    datetime.date objects, so the isinstance branch handles the common case.
    String fallback covers date values quoted in frontmatter.
    """
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        s = raw.strip()
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    raise ValueError(f"Cannot parse date value: {raw!r}")


def _format_date_label(d: date) -> str:
    """Return a human-readable date string, e.g. '30 March 2026'."""
    return f"{d.day} {d.strftime('%B')} {d.year}"


def _render_body(body_md: str) -> tuple[str, str]:
    """Render Markdown body to (body_html, body_text).

    body_html: full HTML for the detail template.
    body_text: tag-stripped plain text used as the client-side search corpus.
    """
    md = _md.Markdown(extensions=["fenced_code", "tables"])
    body_html = md.convert(body_md)
    body_text = " ".join(_STRIP_TAGS.sub(" ", body_html).split())
    return body_html, body_text


def _parse_entry(path: pathlib.Path) -> UpdateEntry:
    """Parse a single Markdown file into an UpdateEntry.

    Raises ValueError when required frontmatter fields (title, date) are
    absent or the date field cannot be parsed to a date object.
    """
    post = frontmatter.load(str(path))

    title = post.get("title")
    raw_date = post.get("date")

    if not title or raw_date is None:
        raise ValueError(
            f"Missing required frontmatter field(s) 'title' / 'date' in {path.name}"
        )

    published_at = _normalize_date(raw_date)
    body_html, body_text = _render_body(post.content)

    return UpdateEntry(
        slug=_make_slug(path),
        title=str(title),
        published_at=published_at,
        published_label=_format_date_label(published_at),
        tags=[str(t) for t in (post.get("tags") or [])],
        summary=str(post.get("summary") or ""),
        body_markdown=post.content,
        body_html=body_html,
        body_text=body_text,
        draft=bool(post.get("draft") or False),
        source_path=path,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_entry(path: pathlib.Path) -> UpdateEntry | None:
    """Parse one Markdown file and return an UpdateEntry, or None on failure.

    Any exception raised by _parse_entry (missing fields, bad date, unreadable
    file) is caught and silently discarded so a single bad file never prevents
    the rest of the feed from loading.
    """
    try:
        return _parse_entry(path)
    except Exception:
        return None


def load_all_entries(
    content_dir: pathlib.Path | None = None,
    *,
    include_drafts: bool = False,
) -> list[UpdateEntry]:
    """Scan *content_dir* for .md files and return valid, non-draft entries.

    - Files that fail to parse are silently skipped (FR-011).
    - Entries with ``draft=True`` are excluded unless *include_drafts* is set
      (FR-010).
    - The returned list is in filesystem order; callers are responsible for
      sorting (T006 adds the sorted helper on top of this).
    - *content_dir* defaults to ``content/updates/`` next to this file so the
      production app requires no argument while tests can supply a temp dir.
    """
    directory = content_dir if content_dir is not None else _CONTENT_DIR

    entries: list[UpdateEntry] = []
    for path in sorted(directory.glob("*.md")):
        entry = load_entry(path)
        if entry is None:
            continue
        if entry.draft and not include_drafts:
            continue
        entries.append(entry)

    return entries


def get_feed(
    content_dir: pathlib.Path | None = None,
    *,
    newest_first: bool = True,
) -> list[UpdateEntry]:
    """Return all published entries sorted by publication date.

    - *newest_first=True* (default) → descending order, most recent at index 0.
    - *newest_first=False* → ascending order, oldest at index 0.
    - Entries that share the same date are secondarily sorted by slug so the
      order is deterministic across runs.
    - *content_dir* is forwarded to ``load_all_entries``; pass a temp directory
      in tests to control the content set.
    """
    entries = load_all_entries(content_dir)
    return sorted(
        entries,
        key=lambda e: (e.published_at, e.slug),
        reverse=newest_first,
    )


def get_available_tags(entries: list[UpdateEntry]) -> list[str]:
    """Return a sorted, deduplicated list of tags from *entries*.

    Accepts a pre-loaded entry list rather than re-scanning the filesystem so
    the feed template can call ``get_feed`` once and derive tags from the same
    snapshot without a second directory scan.
    """
    seen: set[str] = set()
    for entry in entries:
        seen.update(entry.tags)
    return sorted(seen)


def get_entry_by_slug(
    slug: str,
    content_dir: pathlib.Path | None = None,
) -> UpdateEntry | None:
    """Return the published entry whose slug matches *slug*, or None.

    Used by the detail route to look up a single entry.  Draft entries are
    excluded; requesting a draft slug returns None so the route can 404.
    """
    for entry in load_all_entries(content_dir):
        if entry.slug == slug:
            return entry
    return None
