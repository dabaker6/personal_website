from __future__ import annotations

from copy import deepcopy
from typing import Any


SITE_CONTENT: dict[str, Any] = {
    "site": {
        "name": "David Baker",
        "role": "Product-minded engineer",
        "tagline": "Built with GitHub spec kit and flask",
        "description": (
            "An experienced full stack developer with a passion for clean design and reliable systems. "
        ),
        "location": "",
        "year": 2026,
    },
    "navigation": [
        {"label": "Home", "endpoint": "home", "slug": "home"},
        {"label": "About", "endpoint": "about", "slug": "about"},
        {"label": "Contact", "endpoint": "contact", "slug": "contact"},
        {"label": "Updates", "endpoint": "updates", "slug": "updates"},
        {"label": "Matches", "endpoint": "matches", "slug": "matches"},
    ],
    "pages": {
        "home": {
            "title": "Modern personal website",
            "meta_description": (
                "A sleek, server-rendered personal website built with Flask and "
                "designed to grow cleanly over time."
            ),
            "eyebrow": "Personal website",
            "hero_title": "Modern presentation, grounded in dependable engineering.",
            "hero_body": (
                "This site introduces who I am, what I care about, and how I build. "
                "It is intentionally lightweight today and structured to welcome new "
                "pages and backend-backed features later."
            ),
            "primary_cta": {"label": "Read the story", "endpoint": "about"},
            "secondary_cta": {"label": "See contact options", "endpoint": "contact"},
            "highlights": [
                {
                    "title": "Clear positioning",
                    "body": "A direct introduction that helps visitors understand the focus of the site within seconds.",
                },
                {
                    "title": "Responsive by default",
                    "body": "The layout is designed to stay readable and composed on both mobile and desktop screens.",
                },
                {
                    "title": "Extensible structure",
                    "body": "Shared layout, central content, and stable routes make future expansion predictable instead of disruptive.",
                },
                {
                    "title": "Backend search flow",
                    "body": "A Flask-rendered matches experience now connects to a browse API and detail endpoint without relying on client-side app code.",
                },
            ],
            "feature_panels": [
                {
                    "label": "Now",
                    "title": "Introducing the person behind the work",
                    "body": "Landing, about, and contact are the first public surfaces, each rendered on the server and styled as one cohesive system.",
                },
                {
                    "label": "Later",
                    "title": "Ready for growth",
                    "body": "New routes, external services, and richer content can be added without rebuilding the site architecture from scratch.",
                },
            ],
        },
        "about": {
            "title": "About",
            "meta_description": "Background, working style, and the principles behind the site owner.",
            "eyebrow": "About",
            "headline": "I care about restraint, rhythm, and reliable systems.",
            "intro": (
                "My work sits between presentation and implementation. I like interfaces "
                "that feel deliberate, and systems that remain easy to extend after the "
                "first release."
            ),
            "sections": [
                {
                    "title": "Background",
                    "body": "A skilled full stack developer with experience in startups and established companies, focused on building clean, user-friendly products that scale.",
                },
                {
                    "title": "Working style",
                    "body": "Always looking for innovative solutions, but careful to choose the simplest one that gets the job done. I value clear communication and thoughtful design in both code and user experience.",
                },
                {
                    "title": "What this site demonstrates",
                    "body": "A polished personal presence that is responsive now and structurally prepared for future backend integrations later.",
                },
            ],
        },
        "contact": {
            "title": "Contact",
            "meta_description": "Simple public contact options with room for future integrations.",
            "eyebrow": "Contact",
            "headline": "Contact Information",
            "intro": (
                "The first release keeps contact straightforward: public channels only. "
                "If richer workflows arrive later, they can fit into the same structure "
                "without replacing what already works."
            ),
            "fallback_title": "Contact options are being refreshed.",
            "fallback_body": (
                "A direct contact list is not available right now. Please check back "
                "soon for updated public channels."
            ),
        },
    },
    "contact_methods": [
        {
            "label": "Email",
            "value": "d.a.baker246@gmail.com",
            "href": "mailto:d.a.baker246@gmail.com",
            "note": "Best for project conversations and introductions.",
        },
        {
            "label": "GitHub",
            "value": "github.com/dabaker6",
            "href": "https://github.com/dabaker6",
            "note": "Selected code and experiments.",
        },
        {
            "label": "LinkedIn",
            "value": "linkedin.com/in/dabaker246",
            "href": "https://uk.linkedin.com/in/dabaker246",
            "note": "Professional profile and updates.",
        },
    ],
}


def _merge_dicts(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _merge_dicts(base[key], value)
        else:
            base[key] = value
    return base


def get_site_content(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    content = deepcopy(SITE_CONTENT)
    if overrides:
        content = _merge_dicts(content, overrides)
    return content


def get_page(content: dict[str, Any], slug: str) -> dict[str, Any]:
    return content["pages"][slug]
