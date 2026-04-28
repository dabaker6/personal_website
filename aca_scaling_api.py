from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib import error, request


ACA_API_BASE_URL = os.environ.get("ACA_API_BASE_URL", "").rstrip("/")

_ACTIVE_COUNT_RE = re.compile(r"Current active message count:\s*(\d+)", re.IGNORECASE)


class AcaScalingApiError(RuntimeError):
    """Raised when the upstream ACA scaling API cannot satisfy a request."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        active_message_count: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.active_message_count = active_message_count


def _request(path: str, expect_json: bool = True) -> Any:
    """Issue a GET to the ACA API. Returns parsed JSON when *expect_json* is True,
    or the raw response object for callers that only care about status/headers."""
    if not ACA_API_BASE_URL:
        raise AcaScalingApiError("ACA_API_BASE_URL is not configured.")

    url = f"{ACA_API_BASE_URL}{path}"
    req = request.Request(url, method="GET")
    req.add_header("Accept", "application/json")

    try:
        with request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            if not expect_json:
                return None
            return json.loads(body) if body.strip() else None
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}

        if exc.code == 429:
            msg = payload.get("message", "")
            count_match = _ACTIVE_COUNT_RE.search(msg)
            active_count = int(count_match.group(1)) if count_match else None
            raise AcaScalingApiError(
                payload.get("message", "Too many requests — queue is not empty."),
                status_code=429,
                active_message_count=active_count,
            ) from exc

        raise AcaScalingApiError(
            payload.get("message", f"ACA API error {exc.code}."),
            status_code=exc.code,
        ) from exc
    except error.URLError as exc:
        raise AcaScalingApiError(f"Could not reach ACA API: {exc.reason}") from exc


def get_revision_name() -> str:
    """Return the active Container App revision name."""
    result = _request("/revisionName/")
    if not isinstance(result, str) or not result:
        raise AcaScalingApiError("Unexpected response format for revision name.")
    return result


def get_replica_count(revision_name: str) -> int:
    """Return the current replica count for *revision_name*."""
    result = _request(f"/replicas/{revision_name}")
    if not isinstance(result, int):
        raise AcaScalingApiError("Unexpected response format for replica count.")
    return result


def get_queue_length() -> int:
    """Return the current active message count in the Service Bus queue."""
    result = _request("/queue-length/")
    if not isinstance(result, dict):
        raise AcaScalingApiError("Unexpected response format for queue length.")
    raw = result.get("activeMessageCount", "0")
    try:
        return int(raw)
    except (ValueError, TypeError) as exc:
        raise AcaScalingApiError(f"Could not parse queue length value: {raw!r}") from exc


def send_messages(count: int) -> int:
    """Enqueue *count* messages. Returns the accepted message count."""
    _request(f"/send-message/{count}", expect_json=False)
    return count
