"""Property-based and unit tests for education API endpoints.

# Feature: local-web-viewer
# Tests Properties 15–16 from the design document.

Tests the WebsiteServer education API endpoints for JSON structure
consistency and error handling using a real HTTP test server.
"""

from __future__ import annotations

import http.server
import json
import threading
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from codomyrmex.website.server import WebsiteServer
from codomyrmex.website.data_provider import DataProvider


# ── Test server fixture ────────────────────────────────────────────

@pytest.fixture(scope="module")
def api_server():
    """Start a WebsiteServer on a random port for testing."""
    from pathlib import Path

    WebsiteServer.root_dir = Path(".")
    WebsiteServer.data_provider = DataProvider(root_dir=Path("."))
    # Reset education provider so it gets re-created fresh
    WebsiteServer.education_provider = None

    server = http.server.HTTPServer(("127.0.0.1", 0), WebsiteServer)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


def _api_request(base_url: str, method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    """Make an API request and return (status_code, parsed_json)."""
    url = f"{base_url}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Origin", "http://localhost:8787")
    try:
        with urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


# ── Property 15: API JSON structure consistency ────────────────────
# Feature: local-web-viewer, Property 15: API JSON structure consistency
# Validates: Requirements 6.4

CURRICULUM_NAMES = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_",
                           max_codepoint=127),
    min_size=1,
    max_size=30,
).map(str.strip).filter(lambda s: len(s) > 0)

VALID_LEVELS = st.sampled_from(["beginner", "intermediate", "advanced", "expert"])


@given(name=CURRICULUM_NAMES, level=VALID_LEVELS)
@settings(max_examples=50)
def test_property15_api_json_structure_consistency(api_server: str, name: str, level: str) -> None:
    """Successful API responses SHALL be valid JSON with status field.
    Error responses SHALL contain status='error' and non-empty message."""
    # Successful: create curriculum
    status, data = _api_request(api_server, "POST", "/api/education/curricula", {"name": name, "level": level})

    # First call should succeed (201-ish) or conflict if name reused across examples
    assert isinstance(data, dict)
    if status == 200:
        assert data.get("status") == "ok"
        assert "data" in data
    elif status == 409:
        assert data.get("status") == "error"
        assert isinstance(data.get("message"), str)
        assert len(data["message"]) > 0

    # Successful: list curricula
    status2, data2 = _api_request(api_server, "GET", "/api/education/curricula")
    assert status2 == 200
    assert isinstance(data2, dict)
    assert data2.get("status") == "ok"

    # Error: invalid JSON body
    url = f"{api_server}/api/education/curricula"
    req = Request(url, data=b"not-json", method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Origin", "http://localhost:8787")
    try:
        with urlopen(req) as resp:
            err_data = json.loads(resp.read().decode("utf-8"))
            err_status = resp.status
    except HTTPError as e:
        err_data = json.loads(e.read().decode("utf-8"))
        err_status = e.code
    assert err_status == 400
    assert err_data.get("status") == "error"
    assert len(err_data.get("message", "")) > 0


# ── Property 16: Nonexistent resource returns error ────────────────
# Feature: local-web-viewer, Property 16: Nonexistent resource returns error
# Validates: Requirements 6.5


@given(fake_name=CURRICULUM_NAMES)
@settings(max_examples=50)
def test_property16_nonexistent_resource_returns_error(api_server: str, fake_name: str) -> None:
    """Requesting a nonexistent resource SHALL return 404 with descriptive error."""
    # Use a name prefixed to avoid collision with any created curricula
    resource_name = f"__nonexistent__{fake_name}"

    status, data = _api_request(api_server, "GET", f"/api/education/curricula/{resource_name}")
    assert status == 404
    assert isinstance(data, dict)
    assert data.get("status") == "error"
    assert isinstance(data.get("message"), str)
    assert len(data["message"]) > 0

    # Nonexistent session progress
    status2, data2 = _api_request(api_server, "GET", f"/api/education/sessions/{resource_name}/progress")
    assert status2 == 404
    assert data2.get("status") == "error"
    assert len(data2.get("message", "")) > 0
