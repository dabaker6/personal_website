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


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _balls_to_overs(balls: int) -> str:
    completed = balls // 6
    remainder = balls % 6
    return f"{completed}.{remainder}"


def build_scorecard_preview(detail: dict[str, Any]) -> list[dict[str, Any]]:
    """Build a lightweight, presentation-ready scorecard preview per innings."""
    document = detail.get("document", {}) if isinstance(detail, dict) else {}
    innings_data = document.get("innings", []) if isinstance(document, dict) else []
    if not isinstance(innings_data, list):
        return []

    scorecard: list[dict[str, Any]] = []
    for idx, innings in enumerate(innings_data, start=1):
        if not isinstance(innings, dict):
            continue

        team = str(innings.get("team", "")) or f"Innings {idx}"
        overs = innings.get("overs", [])
        if not isinstance(overs, list):
            overs = []

        innings_total = 0
        wickets_lost = 0
        legal_balls = 0

        extras = {"b": 0, "lb": 0, "w": 0, "nb": 0, "p": 0}
        batting: dict[str, dict[str, Any]] = {}
        bowling: dict[str, dict[str, Any]] = {}
        fall_of_wickets: list[str] = []

        for over in overs:
            deliveries = over.get("deliveries", []) if isinstance(over, dict) else []
            if not isinstance(deliveries, list):
                continue

            for delivery in deliveries:
                if not isinstance(delivery, dict):
                    continue

                runs = delivery.get("runs", {}) if isinstance(delivery.get("runs", {}), dict) else {}
                total_runs = _to_int(runs.get("total"))
                batter_runs = _to_int(runs.get("batter"))
                innings_total += total_runs

                delivery_extras = delivery.get("extras", {}) if isinstance(delivery.get("extras", {}), dict) else {}
                wides = _to_int(delivery_extras.get("wides"))
                noballs = _to_int(delivery_extras.get("noballs"))
                byes = _to_int(delivery_extras.get("byes"))
                legbyes = _to_int(delivery_extras.get("legbyes"))
                penalties = _to_int(delivery_extras.get("penalty"))

                extras["w"] += wides
                extras["nb"] += noballs
                extras["b"] += byes
                extras["lb"] += legbyes
                extras["p"] += penalties

                is_legal = wides == 0 and noballs == 0
                if is_legal:
                    legal_balls += 1

                batter_name = str(delivery.get("batter", ""))
                if batter_name:
                    batter_row = batting.setdefault(
                        batter_name,
                        {
                            "name": batter_name,
                            "dismissal": "not out",
                            "runs": 0,
                            "balls": 0,
                            "fours": 0,
                            "sixes": 0,
                        },
                    )
                    batter_row["runs"] += batter_runs
                    if is_legal:
                        batter_row["balls"] += 1
                    if batter_runs == 4:
                        batter_row["fours"] += 1
                    if batter_runs == 6:
                        batter_row["sixes"] += 1

                bowler_name = str(delivery.get("bowler", ""))
                if bowler_name:
                    bowler_row = bowling.setdefault(
                        bowler_name,
                        {
                            "name": bowler_name,
                            "balls": 0,
                            "maidens": 0,
                            "runs": 0,
                            "wickets": 0,
                        },
                    )
                    if is_legal:
                        bowler_row["balls"] += 1
                    bowler_row["runs"] += max(0, total_runs - byes - legbyes)

                wickets = delivery.get("wickets", []) if isinstance(delivery.get("wickets", []), list) else []
                for wicket in wickets:
                    if not isinstance(wicket, dict):
                        continue
                    wickets_lost += 1
                    player_out = str(wicket.get("player_out", ""))
                    kind = str(wicket.get("kind", "wicket"))

                    # Keep dismissal text compact for scorecard rows.
                    dismissal = kind
                    fielders = wicket.get("fielders", []) if isinstance(wicket.get("fielders", []), list) else []
                    if fielders and isinstance(fielders[0], dict) and fielders[0].get("name"):
                        dismissal = f"{kind} ({fielders[0]['name']})"

                    if player_out in batting:
                        batting[player_out]["dismissal"] = dismissal

                    if bowler_name and kind not in {"run out", "retired hurt", "obstructing the field"}:
                        bowling[bowler_name]["wickets"] += 1

                    over_number = _to_int(over.get("over")) if isinstance(over, dict) else 0
                    ball_number = (legal_balls % 6) or 6
                    fall_of_wickets.append(
                        f"{wickets_lost}-{innings_total} ({player_out}, {over_number}.{ball_number})"
                    )

        # Approximate maidens by over-level conceded runs ignoring byes/leg byes.
        for over in overs:
            if not isinstance(over, dict):
                continue
            deliveries = over.get("deliveries", []) if isinstance(over.get("deliveries", []), list) else []
            if len(deliveries) == 0:
                continue

            bowlers_in_over = [str(d.get("bowler", "")) for d in deliveries if isinstance(d, dict)]
            if not bowlers_in_over:
                continue
            over_bowler = bowlers_in_over[0]

            legal_in_over = 0
            conceded_in_over = 0
            for delivery in deliveries:
                if not isinstance(delivery, dict):
                    continue
                runs = delivery.get("runs", {}) if isinstance(delivery.get("runs", {}), dict) else {}
                delivery_extras = delivery.get("extras", {}) if isinstance(delivery.get("extras", {}), dict) else {}
                wides = _to_int(delivery_extras.get("wides"))
                noballs = _to_int(delivery_extras.get("noballs"))
                byes = _to_int(delivery_extras.get("byes"))
                legbyes = _to_int(delivery_extras.get("legbyes"))
                if wides == 0 and noballs == 0:
                    legal_in_over += 1
                conceded_in_over += max(0, _to_int(runs.get("total")) - byes - legbyes)

            if legal_in_over == 6 and conceded_in_over == 0 and over_bowler in bowling:
                bowling[over_bowler]["maidens"] += 1

        batting_rows = list(batting.values())
        for row in batting_rows:
            balls = row["balls"]
            row["sr"] = f"{(row['runs'] * 100 / balls):.1f}" if balls else "-"

        bowling_rows = list(bowling.values())
        for row in bowling_rows:
            row["overs"] = _balls_to_overs(row["balls"])
            balls = row["balls"]
            row["econ"] = f"{(row['runs'] * 6 / balls):.2f}" if balls else "-"

        extras_total = sum(extras.values())
        scorecard.append(
            {
                "team": team,
                "innings_number": idx,
                "title": f"{team} innings",
                "total": innings_total,
                "wickets": wickets_lost,
                "overs": _balls_to_overs(legal_balls),
                "run_rate": f"{(innings_total * 6 / legal_balls):.2f}" if legal_balls else "-",
                "batting": batting_rows,
                "bowling": bowling_rows,
                "extras": {
                    "total": extras_total,
                    "breakdown": extras,
                },
                "fall_of_wickets": fall_of_wickets,
            }
        )

    return scorecard
