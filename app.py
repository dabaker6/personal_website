from __future__ import annotations

from typing import Any

from flask import Flask, render_template

from updates import get_feed, get_available_tags

from content import get_page, get_site_content


def create_app(content_overrides: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    site_content = get_site_content(content_overrides)

    @app.context_processor
    def inject_site_context() -> dict[str, Any]:
        return {
            "site": site_content["site"],
            "navigation": site_content["navigation"],
            "contact_methods": site_content.get("contact_methods", []),
        }

    @app.route("/")
    def home() -> str:
        return render_template(
            "index.html",
            page=get_page(site_content, "home"),
            page_name="home",
        )

    @app.route("/about")
    def about() -> str:
        return render_template(
            "about.html",
            page=get_page(site_content, "about"),
            page_name="about",
        )

    @app.route("/contact")
    def contact() -> str:
        return render_template(
            "contact.html",
            page=get_page(site_content, "contact"),
            page_name="contact",
        )

    @app.route("/updates")
    def updates() -> str:
        feed = get_feed()
        page = {
            "title": "Updates",
            "meta_description": "Blog-style updates, release notes, and build logs.",
            "eyebrow": "Updates",
            "headline": "Notes from the build log",
            "intro": (
                "Recent progress, release notes, and implementation details. "
                "Entries are listed newest first and can be filtered client-side."
            ),
        }

        return render_template(
            "updates.html",
            page=page,
            page_name="updates",
            entries=feed,
            available_tags=get_available_tags(feed),
            default_sort="newest",
            empty_state_title="No updates published yet.",
            empty_filter_title="No entries found.",
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
