from __future__ import annotations

import pathlib
import textwrap

import pytest
from jinja2 import ChoiceLoader, DictLoader

from app import create_app
from updates import get_feed, load_all_entries


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as test_client:
        yield test_client


def test_home_route_returns_server_rendered_html(client):
    response = client.get("/")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "<!doctype html>" in text.lower()
    assert "Modern presentation, grounded in dependable engineering." in text
    assert "Home" in text
    assert "About" in text
    assert "Contact" in text
    assert "Updates" in text
    assert "Matches" in text


@pytest.mark.parametrize(
    ("route", "marker"),
    [
        ("/about", "I care about restraint, rhythm, and reliable systems."),
        ("/contact", "The first release keeps contact straightforward: public channels only."),
    ],
)
def test_secondary_routes_render_expected_content(client, route, marker):
    response = client.get(route)

    assert response.status_code == 200
    assert marker in response.get_data(as_text=True)


def test_contact_page_has_fallback_when_methods_are_missing():
    app = create_app({"contact_methods": []})
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/contact")

    assert response.status_code == 200
    assert "Contact options are being refreshed." in response.get_data(as_text=True)


def test_updates_route_renders_nav_and_newest_first_feed_order():
    app = create_app()
    app.config.update(TESTING=True)
    app.jinja_loader = ChoiceLoader(
        [
            DictLoader(
                {
                    "updates.html": """
{% extends "base.html" %}
{% block content %}
<section>
  <h1>Updates</h1>
  {% for entry in entries %}
  <article data-slug="{{ entry.slug }}">
    <h2>{{ entry.title }}</h2>
    <p>{{ entry.published_label }}</p>
  </article>
  {% endfor %}
</section>
{% endblock %}
"""
                }
            ),
            app.jinja_loader,
        ]
    )

    with app.test_client() as client:
        response = client.get("/updates")

    assert response.status_code == 200
    text = response.get_data(as_text=True)

    assert "Home" in text
    assert "About" in text
    assert "Contact" in text
    assert "Updates" in text
    assert "Matches" in text
    assert "Updates page added" in text
    assert "Site is live" in text

    # Feed defaults to newest-first ordering.
    assert text.index("Updates page added") < text.index("Site is live")


def test_update_detail_route_renders_expected_entry():
    app = create_app()
    app.config.update(TESTING=True)
    app.jinja_loader = ChoiceLoader(
        [
            DictLoader(
                {
                    "update_detail.html": """
{% extends "base.html" %}
{% block content %}
<article>
  <h1>{{ entry.title }}</h1>
  <p>{{ entry.published_label }}</p>
  <div>{{ entry.body_html|safe }}</div>
</article>
{% endblock %}
"""
                }
            ),
            app.jinja_loader,
        ]
    )

    with app.test_client() as client:
        response = client.get("/updates/2026-03-31-updates-page")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Updates page added" in text
    assert "31 March 2026" in text


def test_update_detail_route_returns_404_for_missing_slug(client):
    response = client.get("/updates/does-not-exist")

    assert response.status_code == 404


def test_updates_feed_exposes_search_and_filter_markers_for_client_side_behavior(client):
    response = client.get("/updates")

    assert response.status_code == 200
    text = response.get_data(as_text=True)

    # Search control needed by upcoming client-side filtering script.
    assert 'id="updates-search"' in text

    # Tag controls container + at least one concrete tag control hook.
    assert 'data-role="tag-controls"' in text
    assert 'data-tag="release"' in text

    # Per-entry searchable corpus marker used by the client-side search pass.
    assert 'data-search-text=' in text


def test_updates_feed_exposes_sort_control_for_client_side_behavior(client):
    response = client.get("/updates")

    assert response.status_code == 200
    text = response.get_data(as_text=True)

    # Sort controls container present and wired for JS behaviour.
    assert 'data-role="sort-controls"' in text

    # Both sort options must be present.
    assert 'data-sort="newest"' in text
    assert 'data-sort="oldest"' in text

    # Default sort is newest-first.
    assert 'data-sort="newest" aria-pressed="true"' in text


def test_matches_route_renders_form_controls(client):
    response = client.get("/matches")

    assert response.status_code == 200
    text = response.get_data(as_text=True)

    assert "Browse and inspect matches" in text
    assert 'name="gender"' in text
    assert 'name="fromDate"' in text
    assert 'name="toDate"' in text
    assert 'name="matchType"' in text
    assert 'name="venue"' in text
    assert 'name="eventName"' in text
    assert 'name="team"' in text


def test_matches_route_shows_results_from_browse_api(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)

    def _fake_browse(query):
        assert query.gender == "male"
        return (
            [
                type("Summary", (), {
                    "match_id": "abc123",
                    "teams": ["England", "India"],
                    "venue": "M Chinnaswamy Stadium",
                    "competition": "England tour of India",
                    "date": "2001-12-19",
                })()
            ],
            False,
            1,
        )

    monkeypatch.setattr("app.browse_matches", _fake_browse)

    with app.test_client() as client:
        response = client.get("/matches?gender=male")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "England vs India" in text
    assert "View match summary" in text


def test_match_detail_route_renders_info_summary(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)

    monkeypatch.setattr("app.get_match_detail", lambda _: {"document": {"info": {}}})
    monkeypatch.setattr(
        "app.build_info_summary",
        lambda match_id, _detail: type("Summary", (), {
            "match_id": match_id,
            "event_name": "England tour of India",
            "match_type": "Test",
            "gender": "male",
            "venue": "M Chinnaswamy Stadium",
            "city": "Bengaluru",
            "team_a": "England",
            "team_b": "India",
            "start_date": "2001-12-19",
            "end_date": "2001-12-23",
            "outcome": "Result: draw",
        })(),
    )

    with app.test_client() as client:
        response = client.get("/matches/abc123")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "England tour of India" in text
    assert "England vs India" in text
    assert "Result: draw" in text


def test_match_detail_route_handles_upstream_error(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)

    from matches_api import MatchesApiError

    def _raise_error(_match_id):
        raise MatchesApiError("Provider unavailable", status_code=503)

    monkeypatch.setattr("app.get_match_detail", _raise_error)

    with app.test_client() as client:
        response = client.get("/matches/abc123")

    assert response.status_code == 502
    assert "Provider unavailable" in response.get_data(as_text=True)


# ---------------------------------------------------------------------------
# US5: content loader resilience (draft exclusion + malformed-file safety)
# ---------------------------------------------------------------------------

def test_draft_entry_is_excluded_from_public_feed(tmp_path: pathlib.Path):
    """Entries with draft: true must not appear in the public feed."""
    (tmp_path / "published.md").write_text(
        textwrap.dedent("""\
            ---
            title: Published post
            date: 2026-03-30
            ---
            Body text here.
        """),
        encoding="utf-8",
    )
    (tmp_path / "draft-post.md").write_text(
        textwrap.dedent("""\
            ---
            title: Draft post
            date: 2026-03-31
            draft: true
            ---
            Work in progress.
        """),
        encoding="utf-8",
    )

    entries = get_feed(content_dir=tmp_path)

    slugs = [e.slug for e in entries]
    assert "published" in slugs
    assert "draft-post" not in slugs


def test_malformed_entry_is_skipped_without_raising(tmp_path: pathlib.Path):
    """A file missing required frontmatter fields must be silently skipped."""
    (tmp_path / "valid.md").write_text(
        textwrap.dedent("""\
            ---
            title: Valid post
            date: 2026-03-30
            ---
            Body text here.
        """),
        encoding="utf-8",
    )
    # Missing both title and date — _parse_entry raises ValueError.
    (tmp_path / "malformed.md").write_text(
        textwrap.dedent("""\
            ---
            summary: No title or date here
            ---
            This file has no required frontmatter.
        """),
        encoding="utf-8",
    )

    # Should not raise; malformed file is silently dropped.
    entries = load_all_entries(content_dir=tmp_path)

    assert len(entries) == 1
    assert entries[0].slug == "valid"
