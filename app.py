from __future__ import annotations

from typing import Any

from flask import Flask, abort, render_template, request, url_for

from dotenv import load_dotenv

from updates import get_available_tags, get_entry_by_slug, get_feed

from content import get_page, get_site_content
from matches_api import (
    BrowseQuery,
    MatchesApiError,
    build_progression_series,
    build_scorecard_preview,
    build_wicket_marker_view_model,
    browse_matches,
    build_info_summary,
    format_date_range,
    get_graph_availability,
    get_match_detail,
    is_limited_overs_match_detail,
)


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

    @app.route("/updates/<slug>")
    def update_detail(slug: str) -> str:
        entry = get_entry_by_slug(slug)
        if entry is None:
            abort(404)

        return render_template(
            "update_detail.html",
            page={
                "title": entry.title,
                "meta_description": entry.summary or entry.title,
            },
            page_name="updates",
            entry=entry,
        )

    @app.route("/matches")
    def matches() -> str:
        query = BrowseQuery.from_args(request.args.to_dict(flat=True))
        matches_list = []
        has_more = False
        total_matched = None
        error_message = None

        if query.has_filters():
            try:
                matches_list, has_more, total_matched = browse_matches(query)
            except MatchesApiError as exc:
                error_message = str(exc)

        return render_template(
            "matches.html",
            page={
                "title": "Matches",
                "meta_description": "Search matches with backend API filters and view match summaries.",
                "eyebrow": "Matches",
                "headline": "Browse and inspect matches",
                "intro": "Use filters to find matches, then select a result to view a short summary from match info.",
            },
            page_name="matches",
            query=query,
            matches=matches_list,
            has_more=has_more,
            total_matched=total_matched,
            error_message=error_message,
        )

    @app.route("/matches/<match_id>")
    def match_detail(match_id: str) -> str:
        query = BrowseQuery.from_args(request.args.to_dict(flat=True))
        graph_model = {
            "availability": "unavailable",
            "is_limited_overs": False,
            "series": [],
            "wickets": [],
        }

        try:
            detail = get_match_detail(match_id)
            summary = build_info_summary(match_id, detail)
            scorecard = build_scorecard_preview(detail)
            graph_model = {
                "availability": get_graph_availability(detail),
                "is_limited_overs": is_limited_overs_match_detail(detail),
                "series": build_progression_series(detail),
                "wickets": build_wicket_marker_view_model(detail),
            }
        except MatchesApiError as exc:
            status_code = 504 if exc.status_code == 504 else 502
            return render_template(
                "match_detail.html",
                page={
                    "title": "Match detail unavailable",
                    "meta_description": "Unable to load selected match summary.",
                },
                page_name="matches",
                match_id=match_id,
                summary=None,
                scorecard=[],
                error_message=str(exc),
                query=query,
                format_date_range=format_date_range,
                graph_model=graph_model,
                back_url=url_for("matches", **query.to_query_params()),
            ), status_code

        return render_template(
            "match_detail.html",
            page={
                "title": f"Match {match_id}",
                "meta_description": "Brief summary from the match document info section.",
            },
            page_name="matches",
            match_id=match_id,
            summary=summary,
            scorecard=scorecard,
            error_message=None,
            query=query,
            format_date_range=format_date_range,
            graph_model=graph_model,
            back_url=url_for("matches", **query.to_query_params()),
        )

    return app

load_dotenv()  # Load environment variables from .env file

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
