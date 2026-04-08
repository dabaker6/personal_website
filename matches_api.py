from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib import error, parse, request
import json


BROWSE_QUERY_FIELDS = (
    "gender",
    "fromDate",
    "toDate",
    "venue",
    "matchType",
    "eventName",
    "team",
)


class MatchesApiError(RuntimeError):
    """Raised when the upstream matches API cannot satisfy a request."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class BrowseQuery:
    gender: str = ""
    fromDate: str = ""
    toDate: str = ""
    venue: str = ""
    matchType: str = ""
    eventName: str = ""
    team: str = ""

    @classmethod
    def from_args(cls, args: dict[str, str]) -> "BrowseQuery":
        values = {field: args.get(field, "").strip() for field in BROWSE_QUERY_FIELDS}
        return cls(**values)

    def to_query_params(self) -> dict[str, str]:
        return {field: getattr(self, field) for field in BROWSE_QUERY_FIELDS if getattr(self, field)}

    def has_filters(self) -> bool:
        return any(getattr(self, field) for field in BROWSE_QUERY_FIELDS)


@dataclass(frozen=True)
class MatchSummary:
    match_id: str
    teams: list[str]
    venue: str
    competition: str
    date: str


@dataclass(frozen=True)
class MatchInfoSummary:
    match_id: str
    event_name: str
    match_type: str
    gender: str
    venue: str
    city: str
    team_a: str
    team_b: str
    start_date: str
    end_date: str
    outcome: str


def _api_base_url() -> str:    
    return os.environ.get("MATCHES_API_BASE_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")


def _fetch_json(path: str, query: dict[str, str] | None = None) -> dict[str, Any]:
    base = _api_base_url()
    url = f"{base}{path}"
    if query:
        url = f"{url}?{parse.urlencode(query)}"

    req = request.Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with request.urlopen(req, timeout=10) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except error.HTTPError as exc:
        message = f"Matches API request failed with status {exc.code}."
        try:
            payload = exc.read().decode("utf-8")
            data = json.loads(payload)
            if isinstance(data, dict) and data.get("message"):
                message = str(data["message"])
        except Exception:
            pass
        raise MatchesApiError(message, status_code=exc.code) from exc
    except error.URLError as exc:
        raise MatchesApiError("Unable to reach the matches API right now.") from exc


def browse_matches(query: BrowseQuery) -> tuple[list[MatchSummary], bool, int | None]:
    data = _fetch_json("/matches/browse", query.to_query_params())
    items = data.get("items", [])
    summaries: list[MatchSummary] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        summaries.append(
            MatchSummary(
                match_id=str(item.get("matchId", "")),
                teams=[str(team) for team in item.get("teams", [])],
                venue=str(item.get("venue", "")),
                competition=str(item.get("competition", "")),
                date=str(item.get("date", "")),
            )
        )
    return summaries, bool(data.get("hasMore", False)), data.get("totalMatched")


def get_match_detail(match_id: str) -> dict[str, Any]:
    return _fetch_json(f"/matches/{parse.quote(match_id, safe='')}")


def build_info_summary(match_id: str, detail: dict[str, Any]) -> MatchInfoSummary:
    document = detail.get("document", {}) if isinstance(detail, dict) else {}
    info = document.get("info", {}) if isinstance(document, dict) else {}

    dates = info.get("dates", []) if isinstance(info.get("dates", []), list) else []
    start_date = str(dates[0]) if dates else ""
    end_date = str(dates[-1]) if dates else ""

    teams = info.get("teams", []) if isinstance(info.get("teams", []), list) else []
    team_a = str(teams[0]) if len(teams) >= 1 else ""
    team_b = str(teams[1]) if len(teams) >= 2 else ""

    outcome_data = info.get("outcome", {}) if isinstance(info.get("outcome", {}), dict) else {}
    outcome_parts: list[str] = []
    winner = outcome_data.get("winner")
    if winner:
        outcome_parts.append(f"Winner: {winner}")
    result = outcome_data.get("result")
    if result:
        outcome_parts.append(f"Result: {result}")

    event_data = info.get("event", {}) if isinstance(info.get("event", {}), dict) else {}

    return MatchInfoSummary(
        match_id=match_id,
        event_name=str(event_data.get("name", "")),
        match_type=str(info.get("match_type", "")),
        gender=str(info.get("gender", "")),
        venue=str(info.get("venue", "")),
        city=str(info.get("city", "")),
        team_a=team_a,
        team_b=team_b,
        start_date=start_date,
        end_date=end_date,
        outcome=" | ".join(outcome_parts),
    )


def format_date_range(start: str, end: str) -> str:
    if not start and not end:
        return ""

    def _format(value: str) -> str:
        try:
            parsed = date.fromisoformat(value)
            return parsed.strftime("%d %b %Y")
        except ValueError:
            return value

    if start == end:
        return _format(start)
    return f"{_format(start)} to {_format(end)}"
