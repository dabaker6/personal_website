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
    assert "Cricket Data" in text


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
    assert "Cricket Data" in text
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


# ---------------------------------------------------------------------------
# 004-limited-overs-graph: route-level regression coverage
# ---------------------------------------------------------------------------

def _make_detail(match_type: str, innings_data: list) -> dict:
    """Build a minimal match detail payload with the given match type and innings."""
    return {
        "document": {
            "info": {"match_type": match_type, "teams": ["Team A", "Team B"]},
            "innings": innings_data,
        }
    }


def _over(over_index: int, runs: int, wickets: list | None = None) -> dict:
    """Build a minimal over dict with one delivery carrying the given runs."""
    delivery: dict = {"bowler": "B. Owler", "runs": {"total": runs, "batter": runs}}
    if wickets:
        delivery["wickets"] = wickets
    return {"over": over_index, "deliveries": [delivery]}


def _wicket(player_out: str, kind: str = "caught") -> dict:
    return {"player_out": player_out, "kind": kind}


# --- graph availability helpers ---

def test_get_graph_availability_returns_available_for_qualifying_match_with_full_data():
    from matches_api import get_graph_availability

    detail = _make_detail("T20", [
        {"team": "Team A", "overs": [_over(0, 6), _over(1, 8)]},
        {"team": "Team B", "overs": [_over(0, 5), _over(1, 9)]},
    ])
    assert get_graph_availability(detail) == "available"


def test_get_graph_availability_returns_partial_when_one_innings_lacks_overs():
    from matches_api import get_graph_availability

    detail = _make_detail("ODI", [
        {"team": "Team A", "overs": [_over(0, 6)]},
        {"team": "Team B", "overs": []},  # no over-level data
    ])
    assert get_graph_availability(detail) == "partial"


def test_get_graph_availability_returns_unavailable_for_non_qualifying_match():
    from matches_api import get_graph_availability

    detail = _make_detail("Test", [
        {"team": "Team A", "overs": [_over(0, 6)]},
    ])
    assert get_graph_availability(detail) == "unavailable"


def test_get_graph_availability_returns_unavailable_for_qualifying_match_with_no_overs():
    from matches_api import get_graph_availability

    detail = _make_detail("T20", [
        {"team": "Team A", "overs": []},
        {"team": "Team B", "overs": []},
    ])
    assert get_graph_availability(detail) == "unavailable"


# --- progression series shape ---

def test_build_progression_series_produces_one_entry_per_innings():
    from matches_api import build_progression_series

    detail = _make_detail("IT20", [
        {"team": "Team A", "overs": [_over(0, 4), _over(1, 7)]},
        {"team": "Team B", "overs": [_over(0, 3), _over(1, 10)]},
    ])
    series = build_progression_series(detail)
    assert len(series) == 2
    assert series[0]["team"] == "Team A"
    assert series[1]["team"] == "Team B"


def test_build_progression_series_cumulates_runs_across_overs():
    from matches_api import build_progression_series

    detail = _make_detail("T20", [
        {"team": "Team A", "overs": [_over(0, 6), _over(1, 4), _over(2, 8)]},
    ])
    points = build_progression_series(detail)[0]["points"]
    assert len(points) == 3
    assert points[0]["cumulative_runs"] == 6
    assert points[1]["cumulative_runs"] == 10
    assert points[2]["cumulative_runs"] == 18


# --- wicket marker view model ---

def test_build_wicket_marker_view_model_captures_single_wicket():
    from matches_api import build_wicket_marker_view_model

    detail = _make_detail("ODI", [
        {"team": "Team A", "overs": [
            _over(0, 6, wickets=[_wicket("A. Batsman", "lbw")]),
        ]},
    ])
    markers = build_wicket_marker_view_model(detail)
    assert len(markers) == 1
    assert markers[0]["batter"] == "A. Batsman"
    assert markers[0]["dismissal_method"] == "lbw"
    assert markers[0]["bowler"] == "B. Owler"
    assert markers[0]["over"] == 1
    assert markers[0]["index_in_over"] == 1


def test_build_wicket_marker_view_model_handles_multiple_wickets_same_over():
    from matches_api import build_wicket_marker_view_model

    # Build an over with two deliveries, each carrying a wicket.
    two_wicket_over = {
        "over": 3,
        "deliveries": [
            {"bowler": "Bowler One", "runs": {"total": 1}, "wickets": [_wicket("Batter A", "caught")]},
            {"bowler": "Bowler Two", "runs": {"total": 0}, "wickets": [_wicket("Batter B", "bowled")]},
        ],
    }
    detail = _make_detail("T20", [
        {"team": "Team A", "overs": [two_wicket_over]},
    ])
    markers = build_wicket_marker_view_model(detail)
    assert len(markers) == 2
    # Both belong to the same over group.
    assert markers[0]["over"] == 4
    assert markers[1]["over"] == 4
    # Stack indices must differ so the JS renderer can offset same-over markers.
    assert markers[0]["index_in_over"] == 1
    assert markers[1]["index_in_over"] == 2
    assert markers[0]["batter"] == "Batter A"
    assert markers[1]["batter"] == "Batter B"


def test_build_wicket_marker_view_model_tolerates_missing_optional_fields():
    from matches_api import build_wicket_marker_view_model

    # Wicket with no kind; delivery with no bowler.
    sparse_over = {
        "over": 0,
        "deliveries": [
            {"runs": {"total": 2}, "wickets": [{"player_out": "Some Batter"}]},
        ],
    }
    detail = _make_detail("ODI", [
        {"team": "Team A", "overs": [sparse_over]},
    ])
    markers = build_wicket_marker_view_model(detail)
    assert len(markers) == 1
    assert markers[0]["batter"] == "Some Batter"
    # Missing kind should fall back to the default string, not raise.
    assert isinstance(markers[0]["dismissal_method"], str)
    # Missing bowler should produce an empty string, not raise.
    assert isinstance(markers[0]["bowler"], str)


# --- route-level: qualifying match shows graph section ---

def test_match_detail_route_shows_progression_section_for_qualifying_match(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)

    detail = _make_detail("T20", [
        {"team": "Team A", "overs": [_over(0, 6), _over(1, 8)]},
        {"team": "Team B", "overs": [_over(0, 4), _over(1, 11)]},
    ])

    monkeypatch.setattr("app.get_match_detail", lambda _: detail)

    with app.test_client() as client:
        response = client.get("/matches/t20abc")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "data-progression-chart-payload" in text
    assert '"availability": "available"' in text or '"availability":"available"' in text


def test_match_detail_route_omits_progression_section_for_non_qualifying_match(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)

    detail = _make_detail("Test", [
        {"team": "Team A", "overs": [_over(0, 3)]},
    ])

    monkeypatch.setattr("app.get_match_detail", lambda _: detail)

    with app.test_client() as client:
        response = client.get("/matches/testabc")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    # The chart payload script tag must not appear for non-qualifying matches.
    assert "data-progression-chart-payload" not in text
    # The whole progression-stack section must not appear.
    assert "progression-stack" not in text


def test_match_detail_route_shows_partial_fallback_when_one_innings_has_no_overs(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)

    detail = _make_detail("ODI", [
        {"team": "Team A", "overs": [_over(0, 6)]},
        {"team": "Team B", "overs": []},
    ])

    monkeypatch.setattr("app.get_match_detail", lambda _: detail)

    with app.test_client() as client:
        response = client.get("/matches/partial123")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Progression graph partially available" in text
    # Chart section must not render when data is only partial.
    assert "data-progression-chart-payload" not in text


def test_match_detail_route_shows_unavailable_fallback_for_qualifying_match_with_no_overs(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)

    detail = _make_detail("IT20", [
        {"team": "Team A", "overs": []},
        {"team": "Team B", "overs": []},
    ])

    monkeypatch.setattr("app.get_match_detail", lambda _: detail)

    with app.test_client() as client:
        response = client.get("/matches/unavail123")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Progression graph not available" in text
    assert "data-progression-chart-payload" not in text
