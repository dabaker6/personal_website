# Implementation Plan: Cricket API Integration

**Branch**: `003-cricket-api` | **Date**: 2026-04-08 | **Spec**: `/specs/003-cricket-api/spec.md`
**Input**: Feature specification from `/specs/003-cricket-api/spec.md`

**Note**: This plan documents the implementation already applied to the existing Flask personal website.

## Summary

Add a server-rendered Matches section to the existing Flask site that integrates with the backend cricket API. The implementation introduces a dedicated API helper module, a browse route, a match detail route, two templates, incremental CSS additions, navigation updates, and route-level tests. The feature preserves the established visual style and keeps the full browse-to-detail flow in Flask rather than pushing state management into JavaScript.

## Technical Context

**Language/Version**: Python 3.14  
**Primary Dependencies**: Flask, pytest  
**Storage**: No application-owned persistence; data is fetched on demand from the upstream matches API  
**Testing**: pytest with monkeypatched backend calls  
**Target Platform**: Modern desktop and mobile web browsers served by a Python runtime  
**Project Type**: web-service  
**Performance Goals**: Return meaningful HTML on initial response for `/matches` and `/matches/<match_id>`; avoid unnecessary client-side application code; keep upstream requests bounded to a single browse call or detail call per page request  
**Constraints**: Must fit the existing single-app Flask architecture; must preserve the current site look and feel; must use server-rendered templates; should avoid adding unnecessary dependencies for basic HTTP integration; backend availability cannot be guaranteed so graceful error states are required  
**Scale/Scope**: One new top-level site section, two public routes, one small API-integration module, and route-level test coverage for success and degraded behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: The feature is delivered as server-rendered Flask routes that return usable HTML without a client-side application dependency.
- PASS: The implementation stays intentionally small and consistent with the existing architecture: Flask, Jinja templates, shared CSS, and route-level tests.
- PASS: Styling and navigation are additive to the established site instead of introducing a separate design system.
- PASS: Error handling is explicit for upstream dependency failures.
- PASS: No secrets or credentials are committed; the upstream API base URL is provided through environment configuration.

Post-design re-check:

- PASS: The implementation remained within the existing Flask app structure and did not require exceptions to the repository's simplicity rules.

## Project Structure

### Documentation (this feature)

```text
specs/003-cricket-api/
├── checklists/
│   └── requirements.md
├── contracts/
│   └── cricket-routes.md
├── data-model.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md
```

### Source Code (repository root)

```text
app.py
content.py
matches_api.py
README.md
specs/
├── 63963.json
└── openapi.yaml
static/
└── css/
    └── site.css
templates/
├── match_detail.html
└── matches.html
tests/
└── test_routes.py
```

**Structure Decision**: Keep the current single Flask app as the composition point. Add a focused `matches_api.py` integration module for upstream HTTP calls and response shaping. This separates API concerns from route functions while keeping the codebase small and predictable.

## Implementation Notes

- `matches_api.py` owns browse query parsing, upstream HTTP requests, response normalization, and concise info-summary construction.
- `app.py` owns route orchestration, template selection, and high-level error mapping.
- `templates/matches.html` renders the search form and browse results.
- `templates/match_detail.html` renders the info-derived summary for one selected match.
- `static/css/site.css` extends the existing design tokens with matches-specific form and summary styling.
- `tests/test_routes.py` verifies form rendering, browse result rendering, detail rendering, navigation presence, and upstream failure handling.

## Complexity Tracking

No constitutional violations or complexity exceptions were identified. The implementation intentionally used the standard library for upstream HTTP calls instead of introducing another dependency because the integration requirements were limited to simple GET requests and JSON parsing.
