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
