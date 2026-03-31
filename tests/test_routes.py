from __future__ import annotations

import pytest

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
