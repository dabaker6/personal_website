from __future__ import annotations

import pytest
from jinja2 import ChoiceLoader, DictLoader

from app import create_app


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


@pytest.mark.parametrize(
    ("route", "marker"),
    [
        ("/about", "I care about restraint, rhythm, and reliable systems."),
        ("/contact", "Simple public contact, no workflow overhead."),
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
