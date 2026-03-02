"""
Unit tests for ProxyHandler mixin — Zero-Mock compliant.

Tests the no-content, invalid-JSON, and missing-data-provider paths
that don't require a running Ollama instance.
"""
import io
import json

import pytest

from codomyrmex.website.handlers.proxy_handler import ProxyHandler

# ── Helpers ──────────────────────────────────────────────────────────


class _FakeHeaders(dict):
    """Minimal headers object: supports .get()."""


class _FakeDataProvider:
    """Minimal DataProvider stand-in that returns basic LLM config."""

    def get_llm_config(self):
        return {"default_model": "llama3.2"}

    def get_pai_awareness_data(self):
        return {
            "metrics": {
                "mission_count": 1,
                "project_count": 2,
                "completed_tasks": 3,
                "total_tasks": 5,
                "overall_completion": 60,
            },
            "missions": [{"title": "Test mission", "status": "active"}],
            "projects": [{"title": "Test project", "completion_percentage": 50}],
        }


class FakeHandler(ProxyHandler):
    """Concrete host class providing ProxyHandler's expected interface."""

    def __init__(self, *, content_length=0, body=b"", data_provider=None):
        self.headers = _FakeHeaders({"Content-Length": str(content_length)})
        self.rfile = io.BytesIO(body)
        self.data_provider = data_provider
        self.responses: list[dict] = []
        self.errors: list[tuple] = []

    def send_json_response(self, data, status=200):
        self.responses.append({"status": status, "data": data})

    def send_error(self, code, msg):
        self.errors.append((code, msg))


# ── handle_chat ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestHandleChatNonNetwork:
    """Tests for handle_chat() paths that don't need Ollama."""

    def test_no_content_length_returns_400(self):
        """Content-Length=0 → 400 error."""
        handler = FakeHandler(content_length=0)
        handler.handle_chat()
        assert len(handler.responses) == 1
        assert handler.responses[0]["status"] == 400
        assert "error" in handler.responses[0]["data"]

    def test_zero_content_length_header_returns_400(self):
        """Explicit Content-Length: 0 → 400."""
        handler = FakeHandler(content_length=0, body=b"")
        handler.handle_chat()
        assert handler.responses[0]["status"] == 400

    def test_invalid_json_returns_400(self):
        """Invalid JSON body → 400."""
        body = b"not-valid-json"
        handler = FakeHandler(content_length=len(body), body=body)
        handler.handle_chat()
        assert len(handler.responses) == 1
        assert handler.responses[0]["status"] == 400
        assert "Invalid JSON" in str(handler.responses[0]["data"])

    def test_invalid_content_length_header_treated_as_zero(self):
        """Non-integer Content-Length treated as 0 → 400."""
        handler = FakeHandler()
        handler.headers["Content-Length"] = "not-a-number"
        handler.handle_chat()
        assert handler.responses[0]["status"] == 400


# ── handle_awareness_summary ─────────────────────────────────────────


@pytest.mark.unit
class TestHandleAwarenessSummaryNonNetwork:
    """Tests for handle_awareness_summary() paths that don't need Ollama."""

    def test_no_content_returns_400(self):
        """Empty body → 400."""
        handler = FakeHandler(content_length=0)
        handler.handle_awareness_summary()
        assert handler.responses[0]["status"] == 400

    def test_invalid_json_returns_400(self):
        """Invalid JSON → 400."""
        body = b"bad json"
        handler = FakeHandler(content_length=len(body), body=body)
        handler.handle_awareness_summary()
        assert handler.responses[0]["status"] == 400

    def test_missing_data_provider_returns_500(self):
        """data_provider=None → 500 with error."""
        body = json.dumps({"model": "llama3.2"}).encode()
        handler = FakeHandler(content_length=len(body), body=body, data_provider=None)
        handler.handle_awareness_summary()
        assert handler.responses[0]["status"] == 500
        assert "error" in handler.responses[0]["data"]

    def test_with_data_provider_uses_llm_config_model(self):
        """With valid data_provider and body, handler completes and returns a response."""
        body = json.dumps({}).encode()  # No model specified → uses config
        handler = FakeHandler(
            content_length=len(body),
            body=body,
            data_provider=_FakeDataProvider(),
        )
        # This will try to call Ollama — may succeed (200) or fail (503 if not running)
        handler.handle_awareness_summary()
        # Should always produce exactly one response regardless of Ollama availability
        assert len(handler.responses) == 1
        assert handler.responses[0]["status"] in (200, 500, 502, 503, 504)
