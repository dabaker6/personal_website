from __future__ import annotations

import io
import json
from unittest.mock import MagicMock
from urllib import error as urllib_error

import pytest

from aca_scaling_api import (
    AcaScalingApiError,
    get_queue_length,
    get_replica_count,
    get_revision_name,
    send_messages,
)

_BASE = "http://fake-aca.test"


def _mock_response(body) -> MagicMock:
    """Build a mock urlopen context-manager response with the given body."""
    if isinstance(body, str):
        body_bytes = body.encode()
    else:
        body_bytes = json.dumps(body).encode()
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    mock.read.return_value = body_bytes
    return mock


def _http_error(code: int, body: dict | str = "") -> urllib_error.HTTPError:
    """Build a urllib HTTPError whose read() returns the given body bytes."""
    if isinstance(body, dict):
        body_bytes = json.dumps(body).encode()
    else:
        body_bytes = body.encode() if isinstance(body, str) else body
    return urllib_error.HTTPError(
        url=_BASE + "/fake",
        code=code,
        msg="Error",
        hdrs=MagicMock(),
        fp=io.BytesIO(body_bytes),
    )


@pytest.fixture(autouse=True)
def patch_base_url(monkeypatch):
    """Ensure ACA_API_BASE_URL is set for every test in this module."""
    monkeypatch.setattr("aca_scaling_api.ACA_API_BASE_URL", _BASE)


# ── get_revision_name ──────────────────────────────────────────────────────

def test_get_revision_name_returns_string_on_success(monkeypatch):
    monkeypatch.setattr(
        "aca_scaling_api.request.urlopen",
        lambda *a, **kw: _mock_response('"rev-abc-123"'),
    )
    assert get_revision_name() == "rev-abc-123"


def test_get_revision_name_raises_on_404(monkeypatch):
    def _raise(*a, **kw):
        raise _http_error(404, {"message": "Revision not found"})

    monkeypatch.setattr("aca_scaling_api.request.urlopen", _raise)

    with pytest.raises(AcaScalingApiError) as exc_info:
        get_revision_name()
    assert exc_info.value.status_code == 404


# ── get_replica_count ──────────────────────────────────────────────────────

def test_get_replica_count_returns_int_on_success(monkeypatch):
    monkeypatch.setattr(
        "aca_scaling_api.request.urlopen",
        lambda *a, **kw: _mock_response(3),
    )
    assert get_replica_count("rev-abc") == 3


def test_get_replica_count_raises_on_500(monkeypatch):
    def _raise(*a, **kw):
        raise _http_error(500, {"message": "Internal error"})

    monkeypatch.setattr("aca_scaling_api.request.urlopen", _raise)

    with pytest.raises(AcaScalingApiError) as exc_info:
        get_replica_count("rev-abc")
    assert exc_info.value.status_code == 500


# ── get_queue_length ───────────────────────────────────────────────────────

def test_get_queue_length_returns_int_on_success(monkeypatch):
    monkeypatch.setattr(
        "aca_scaling_api.request.urlopen",
        lambda *a, **kw: _mock_response({"activeMessageCount": 42}),
    )
    assert get_queue_length() == 42


def test_get_queue_length_raises_on_500(monkeypatch):
    def _raise(*a, **kw):
        raise _http_error(500, {"message": "Service error"})

    monkeypatch.setattr("aca_scaling_api.request.urlopen", _raise)

    with pytest.raises(AcaScalingApiError) as exc_info:
        get_queue_length()
    assert exc_info.value.status_code == 500


# ── send_messages ──────────────────────────────────────────────────────────

def test_send_messages_returns_count_on_success(monkeypatch):
    monkeypatch.setattr(
        "aca_scaling_api.request.urlopen",
        lambda *a, **kw: _mock_response(""),
    )
    assert send_messages(50) == 50


def test_send_messages_raises_on_400(monkeypatch):
    def _raise(*a, **kw):
        raise _http_error(400, {"message": "Bad request"})

    monkeypatch.setattr("aca_scaling_api.request.urlopen", _raise)

    with pytest.raises(AcaScalingApiError) as exc_info:
        send_messages(0)
    assert exc_info.value.status_code == 400


def test_send_messages_raises_429_with_active_message_count_from_body(monkeypatch):
    body = {"message": "Current active message count: 99 — queue is not empty."}

    def _raise(*a, **kw):
        raise _http_error(429, body)

    monkeypatch.setattr("aca_scaling_api.request.urlopen", _raise)

    with pytest.raises(AcaScalingApiError) as exc_info:
        send_messages(10)
    err = exc_info.value
    assert err.status_code == 429
    assert err.active_message_count == 99


def test_send_messages_raises_on_500(monkeypatch):
    def _raise(*a, **kw):
        raise _http_error(500, {"message": "Server error"})

    monkeypatch.setattr("aca_scaling_api.request.urlopen", _raise)

    with pytest.raises(AcaScalingApiError) as exc_info:
        send_messages(5)
    assert exc_info.value.status_code == 500


def test_send_messages_raises_on_url_error(monkeypatch):
    def _raise(*a, **kw):
        raise urllib_error.URLError("Connection refused")

    monkeypatch.setattr("aca_scaling_api.request.urlopen", _raise)

    with pytest.raises(AcaScalingApiError) as exc_info:
        send_messages(5)
    assert "Connection refused" in str(exc_info.value)
    assert exc_info.value.status_code is None
