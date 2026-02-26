"""
Unit tests for the WebsiteServer class — Zero-Mock compliant.

Tests use a real TCPServer + DataProvider and make real HTTP requests.
Ollama-dependent tests use real Ollama calls and skip when unavailable.
"""

import http.client
import importlib.util
import json
import socketserver
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
import requests as _requests_lib

from codomyrmex.website.data_provider import DataProvider
from codomyrmex.website.server import WebsiteServer


def _ollama_available() -> tuple[bool, str | None]:
    """Return (True, model_name) if Ollama server is reachable and has a model."""
    try:
        resp = _requests_lib.get("http://localhost:11434/api/version", timeout=2)
        if resp.status_code != 200:
            return False, None
        # Find an available model
        tags_resp = _requests_lib.get("http://localhost:11434/api/tags", timeout=2)
        if tags_resp.status_code == 200:
            models = tags_resp.json().get("models", [])
            if models:
                return True, models[0]["name"]
        return False, None
    except Exception:
        return False, None


_OLLAMA_AVAILABLE, _OLLAMA_MODEL = _ollama_available()
_skip_no_ollama = pytest.mark.skipif(
    not _OLLAMA_AVAILABLE, reason="Ollama server not reachable or no models installed"
)

_AGENTIC_MEMORY_AVAILABLE = importlib.util.find_spec("codomyrmex.agentic_memory.mcp_tools") is not None
_skip_no_agentic_memory = pytest.mark.skipif(
    not _AGENTIC_MEMORY_AVAILABLE,
    reason="codomyrmex.agentic_memory.mcp_tools not installed",
)


# ── Helpers ─────────────────────────────────────────────────────────


def _build_project(tmp_path: Path) -> Path:
    """Create a minimal project tree that DataProvider can scan."""
    src = tmp_path / "src" / "codomyrmex"
    src.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    # A module for get_modules
    mod = src / "fake_mod"
    mod.mkdir()
    (mod / "__init__.py").write_text('"""Fake module for testing."""\n')
    (mod / "AGENTS.md").write_text("Agent guide for fake_mod")
    # A config file
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    # A README for docs
    (tmp_path / "README.md").write_text("# Test Project\n")
    return tmp_path


class _LiveServer:
    """Context-like helper wrapping a real TCPServer + WebsiteServer."""

    def __init__(self, root: Path):
        self.root = root
        self.provider = DataProvider(root)
        WebsiteServer.root_dir = root
        WebsiteServer.data_provider = self.provider
        # Allow port reuse across rapid test runs
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), WebsiteServer)
        self.port = self.httpd.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self._thread.start()

    def shutdown(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    # -- convenience request helpers --

    def get(self, path: str) -> tuple[int, dict | list | str]:
        """Make a GET request and return (status, parsed_json)."""
        url = f"{self.base}{path}"
        try:
            resp = urlopen(url, timeout=10)
            body = resp.read().decode()
            return resp.status, json.loads(body)
        except HTTPError as e:
            body = e.read().decode()
            try:
                return e.code, json.loads(body)
            except json.JSONDecodeError:
                return e.code, body

    def post(self, path: str, payload: dict | None = None,
             origin: str | None = "http://127.0.0.1:8787",
             timeout: int = 10) -> tuple[int, dict]:
        """Make a POST request and return (status, parsed_json).

        Uses http.client for reliability with POST requests to avoid
        ConnectionResetError issues with urllib.request.
        """
        body_bytes = json.dumps(payload or {}).encode()
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=timeout)
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        try:
            conn.request("POST", path, body=body_bytes, headers=headers)
            resp = conn.getresponse()
            body = resp.read().decode()
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
        finally:
            conn.close()


@pytest.fixture
def live_server(tmp_path):
    """Yield a running _LiveServer with a real project tree."""
    root = _build_project(tmp_path)
    srv = _LiveServer(root)
    yield srv
    srv.shutdown()


# ── Class-level Config Tests ────────────────────────────────────────


@pytest.mark.unit
class TestWebsiteServerInit:
    """Tests for WebsiteServer class attributes."""

    def test_has_class_level_config(self):
        """Test that class-level configuration attributes exist."""
        assert hasattr(WebsiteServer, "root_dir")
        assert hasattr(WebsiteServer, "data_provider")


# ── GET Endpoint Tests ──────────────────────────────────────────────


@pytest.mark.unit
class TestGETEndpoints:
    """Tests for all GET API endpoints via live HTTP requests."""

    def test_status_endpoint(self, live_server):
        """Test /api/status returns a dict with system information."""
        status, data = live_server.get("/api/status")
        assert status == 200
        assert isinstance(data, dict)
        assert "status" in data

    def test_health_endpoint(self, live_server):
        """Test /api/health returns comprehensive health data."""
        status, data = live_server.get("/api/health")
        assert status == 200
        assert isinstance(data, dict)

    def test_modules_list(self, live_server):
        """Test /api/modules returns module list containing fake_mod."""
        status, data = live_server.get("/api/modules")
        assert status == 200
        assert isinstance(data, list)
        names = [m["name"] for m in data]
        assert "fake_mod" in names

    def test_module_detail(self, live_server):
        """Test /api/modules/{name} returns module detail."""
        status, data = live_server.get("/api/modules/fake_mod")
        assert status == 200
        assert data["name"] == "fake_mod"

    def test_module_detail_404(self, live_server):
        """Test /api/modules/{name} returns 404 for unknown module."""
        status, data = live_server.get("/api/modules/nonexistent_xyz")
        assert status == 404
        assert "error" in data

    def test_agents_list(self, live_server):
        """Test /api/agents returns a list."""
        status, data = live_server.get("/api/agents")
        assert status == 200
        assert isinstance(data, list)

    def test_scripts_list(self, live_server):
        """Test /api/scripts returns a list."""
        status, data = live_server.get("/api/scripts")
        assert status == 200
        assert isinstance(data, list)

    def test_config_list(self, live_server):
        """Test /api/config returns config files including pyproject.toml."""
        status, data = live_server.get("/api/config")
        assert status == 200
        assert isinstance(data, list)
        names = [c["name"] for c in data]
        assert "pyproject.toml" in names

    def test_config_get(self, live_server):
        """Test /api/config/{name} returns file content."""
        status, data = live_server.get("/api/config/pyproject.toml")
        assert status == 200
        assert "content" in data
        assert "test" in data["content"]

    def test_config_get_traversal_blocked(self, live_server):
        """Test /api/config/../../etc/passwd returns 403."""
        status, data = live_server.get("/api/config/../../etc/passwd")
        assert status in (403, 404)

    def test_docs_list(self, live_server):
        """Test /api/docs returns doc tree."""
        status, data = live_server.get("/api/docs")
        assert status == 200
        assert isinstance(data, dict)

    def test_docs_get(self, live_server):
        """Test /api/docs/{path} returns file content."""
        status, data = live_server.get("/api/docs/README.md")
        assert status == 200
        assert "content" in data
        assert "Test Project" in data["content"]

    def test_docs_get_404(self, live_server):
        """Test /api/docs/{path} returns 404 for missing file."""
        status, data = live_server.get("/api/docs/NONEXISTENT_FILE_XYZ.md")
        assert status == 404

    def test_pipelines_list(self, live_server):
        """Test /api/pipelines returns a list."""
        status, data = live_server.get("/api/pipelines")
        assert status == 200
        assert isinstance(data, list)

    def test_awareness_endpoint(self, live_server):
        """Test /api/awareness returns PAI ecosystem data."""
        status, data = live_server.get("/api/awareness")
        assert status == 200
        assert isinstance(data, dict)
        assert "missions" in data
        assert "projects" in data
        assert "mermaid_graph" in data

    def test_llm_config_endpoint(self, live_server):
        """Test /api/llm/config returns LLM configuration."""
        status, data = live_server.get("/api/llm/config")
        assert status == 200
        assert isinstance(data, dict)
        assert "default_model" in data
        assert "preferred_models" in data
        assert "available_models" in data
        assert "ollama_host" in data

    def test_llm_config_returns_available_models(self, live_server):
        """Test that /api/llm/config includes available_models key."""
        status, data = live_server.get("/api/llm/config")
        assert status == 200
        assert isinstance(data["available_models"], list)

    def test_tools_endpoint(self, live_server):
        """Test /api/tools returns MCP tools, resources, and prompts."""
        status, data = live_server.get("/api/tools")
        assert status == 200
        assert isinstance(data, dict)
        assert "tools" in data
        assert "resources" in data
        assert "prompts" in data
        assert isinstance(data["tools"], list)

    def test_tools_have_expected_fields(self, live_server):
        """Test that each tool has name, description, category, is_destructive."""
        status, data = live_server.get("/api/tools")
        assert status == 200
        if data["tools"]:
            tool = data["tools"][0]
            assert "name" in tool
            assert "description" in tool
            assert "category" in tool
            assert "is_destructive" in tool


# ── POST Endpoint Tests ─────────────────────────────────────────────


@pytest.mark.unit
class TestPOSTEndpoints:
    """Tests for POST API endpoints via live HTTP requests."""

    def test_refresh_returns_system_data(self, live_server):
        """Test /api/refresh returns aggregated data."""
        status, data = live_server.post("/api/refresh")
        assert status == 200
        assert "system" in data
        assert "modules" in data
        assert "agents" in data
        assert "scripts" in data

    def test_execute_requires_script_name(self, live_server):
        """Test /api/execute returns 400 when script name is missing."""
        status, data = live_server.post("/api/execute", {})
        assert status == 400

    def test_execute_rejects_path_traversal(self, live_server):
        """Test /api/execute returns 403 for path traversal."""
        status, data = live_server.post("/api/execute", {"script": "../../../etc/passwd"})
        assert status == 403

    def test_execute_rejects_missing_script(self, live_server):
        """Test /api/execute returns 403 for non-existent script."""
        status, data = live_server.post("/api/execute", {"script": "nonexistent_script.py"})
        assert status == 403

    def test_execute_runs_real_script(self, live_server):
        """Test /api/execute can run a real script."""
        script = live_server.root / "scripts" / "hello.py"
        script.write_text('print("hello from test")\n')

        status, data = live_server.post("/api/execute", {"script": "hello.py"})
        assert status == 200
        assert data["success"] is True
        assert "hello from test" in data["stdout"]

    def test_tests_run_endpoint(self, live_server):
        """Test /api/tests endpoint returns 202 Accepted (async background run)."""
        status, data = live_server.post("/api/tests", {})
        assert status == 202
        assert isinstance(data, dict)
        assert data.get("status") == "running"


# ── Security Tests ──────────────────────────────────────────────────


@pytest.mark.unit
class TestOriginValidation:
    """Tests for CORS/CSRF origin validation with live server."""

    def test_valid_localhost_origin(self, live_server):
        """Test that localhost:8787 origin is accepted."""
        status, data = live_server.post(
            "/api/refresh", {}, origin="http://localhost:8787"
        )
        assert status == 200

    def test_valid_127_origin(self, live_server):
        """Test that 127.0.0.1:8787 origin is accepted."""
        status, data = live_server.post(
            "/api/refresh", {}, origin="http://127.0.0.1:8787"
        )
        assert status == 200

    def test_invalid_origin_rejected(self, live_server):
        """Test that evil.com origin is rejected with 403."""
        status, data = live_server.post(
            "/api/refresh", {}, origin="http://evil.com"
        )
        assert status == 403
        assert "error" in data

    def test_no_origin_accepted(self, live_server):
        """Test that requests without Origin header are accepted (curl/same-origin)."""
        status, data = live_server.post("/api/refresh", {}, origin=None)
        assert status == 200


# ── POST Error Handling ─────────────────────────────────────────────


@pytest.mark.unit
class TestPOSTErrorHandling:
    """Tests for POST handler error handling via live HTTP."""

    def test_execute_malformed_json(self, live_server):
        """Test /api/execute with malformed JSON returns 400."""
        req = Request(
            f"{live_server.base}/api/execute",
            data=b"not valid json",
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Origin", "http://127.0.0.1:8787")
        try:
            resp = urlopen(req, timeout=10)
            status = resp.status
        except HTTPError as e:
            status = e.code
        assert status == 400

    def test_chat_missing_content_returns_400(self, live_server):
        """Test /api/chat with empty body returns 400."""
        req = Request(
            f"{live_server.base}/api/chat",
            data=b"",
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Content-Length", "0")
        req.add_header("Origin", "http://127.0.0.1:8787")
        try:
            resp = urlopen(req, timeout=10)
            status = resp.status
        except HTTPError as e:
            status = e.code
        assert status == 400


# ── Config Save Tests ───────────────────────────────────────────────


@pytest.mark.unit
class TestConfigSave:
    """Tests for handle_config_save() via live HTTP."""

    def test_successful_save(self, live_server):
        """Test saving config content returns success."""
        # Create a file to save into
        (live_server.root / "test_config.toml").write_text("original")

        status, data = live_server.post(
            "/api/config",
            {"filename": "test_config.toml", "content": "[updated]\nkey = true\n"},
        )
        assert status == 200
        assert data.get("success") is True

        # Verify actual file was updated
        assert "[updated]" in (live_server.root / "test_config.toml").read_text()

    def test_missing_filename_returns_400(self, live_server):
        """Test that missing filename returns 400."""
        status, data = live_server.post("/api/config", {})
        assert status == 400

    def test_traversal_returns_403(self, live_server):
        """Test that path traversal in filename returns 403."""
        status, data = live_server.post(
            "/api/config",
            {"filename": "../../etc/passwd", "content": "evil"},
        )
        assert status == 403


# ── Chat Endpoint Tests (Ollama mocked — external service) ──────────


@pytest.mark.unit
class TestChatEndpoint:
    """Tests for /api/chat — uses real Ollama when available, skips otherwise."""

    @_skip_no_ollama
    def test_chat_forwards_to_ollama(self, live_server):
        """Test that chat endpoint proxies to Ollama successfully."""
        status, data = live_server.post("/api/chat", {"message": "Hello", "model": _OLLAMA_MODEL}, timeout=90)
        assert status == 200
        assert data["success"] is True
        assert len(data.get("response", "")) > 0

    @_skip_no_ollama
    def test_chat_uses_default_model(self, live_server):
        """Test that chat endpoint uses an available model."""
        status, data = live_server.post("/api/chat", {"message": "Hello", "model": _OLLAMA_MODEL}, timeout=90)
        assert status == 200
        assert data["success"] is True

    def test_chat_connection_error_returns_503(self, live_server):
        """Test that Ollama connection failure returns 503.

        Uses a real POST to an endpoint that should fail when Ollama is down,
        or skips if Ollama is actually running.
        """
        if _OLLAMA_AVAILABLE:
            pytest.skip("Ollama is running — cannot test connection-error path")
        status, data = live_server.post("/api/chat", {"message": "Hello"})
        assert status == 503
        assert "error" in data


# ── Awareness Summary Tests (Ollama mocked) ─────────────────────────


@pytest.mark.unit
class TestAwarenessSummary:
    """Tests for /api/awareness/summary — uses real Ollama when available."""

    @_skip_no_ollama
    def test_ollama_success(self, live_server):
        """Test successful AI summary generation."""
        status, data = live_server.post(
            "/api/awareness/summary", {"model": _OLLAMA_MODEL}, timeout=90
        )
        assert status == 200
        assert data["success"] is True
        assert "summary" in data

    @_skip_no_ollama
    def test_awareness_summary_uses_default_model(self, live_server):
        """Test that awareness summary uses an available model."""
        status, data = live_server.post("/api/awareness/summary", {"model": _OLLAMA_MODEL}, timeout=90)
        assert status == 200
        assert data["success"] is True

    def test_connection_error_returns_503(self, live_server):
        """Test that Ollama connection error returns 503."""
        if _OLLAMA_AVAILABLE:
            pytest.skip("Ollama is running — cannot test connection-error path")
        status, data = live_server.post(
            "/api/awareness/summary", {"model": "llama3"}
        )
        assert status == 503
        assert "error" in data

    def test_missing_body_returns_400(self, live_server):
        """Test that empty POST body returns 400."""
        req = Request(
            f"{live_server.base}/api/awareness/summary",
            data=b"",
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Content-Length", "0")
        req.add_header("Origin", "http://127.0.0.1:8787")
        try:
            resp = urlopen(req, timeout=10)
            status = resp.status
        except HTTPError as e:
            status = e.code
        assert status == 400


# ── Routing Tests ───────────────────────────────────────────────────


@pytest.mark.unit
class TestRouting:
    """Tests for GET/POST routing dispatch via live HTTP."""

    def test_get_status_routes_correctly(self, live_server):
        """Test that GET /api/status resolves."""
        status, _ = live_server.get("/api/status")
        assert status == 200

    def test_get_health_routes_correctly(self, live_server):
        """Test that GET /api/health resolves."""
        status, _ = live_server.get("/api/health")
        assert status == 200

    def test_post_execute_routes_correctly(self, live_server):
        """Test that POST /api/execute resolves (even with invalid body)."""
        status, _ = live_server.post("/api/execute", {})
        assert status == 400  # Missing script name, but routed correctly

    def test_post_tests_routes_correctly(self, live_server):
        """Test that POST /api/tests resolves (202 Accepted for async test runs)."""
        status, data = live_server.post("/api/tests", {})
        assert status in (200, 202)  # 202 Accepted is correct for async test start

    def test_unknown_api_returns_404(self, live_server):
        """Test that unknown API endpoint returns 404."""
        status, _ = live_server.post("/api/nonexistent", {})
        assert status == 404

    def test_get_trust_status_routes_correctly(self, live_server):
        """Test that GET /api/trust/status resolves."""
        status, _ = live_server.get("/api/trust/status")
        assert status == 200

    def test_post_pai_action_routes_correctly(self, live_server):
        """Test that POST /api/pai/action resolves (even with invalid body)."""
        status, _ = live_server.post("/api/pai/action", {})
        assert status == 400  # Empty action, but routed correctly

    def test_get_dispatch_status_routes_correctly(self, live_server):
        """Test that GET /api/agent/dispatch/status resolves."""
        WebsiteServer._dispatch_orch = None
        status, _ = live_server.get("/api/agent/dispatch/status")
        assert status == 200


# ── CORS Preflight Tests ────────────────────────────────────────────


@pytest.mark.unit
class TestCORSPreflight:
    """Tests for do_OPTIONS CORS preflight handler."""

    def test_options_returns_204(self, live_server):
        """Test that OPTIONS request returns 204 No Content."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server.port, timeout=10)
        try:
            conn.request("OPTIONS", "/api/status", headers={"Origin": "http://localhost:8787"})
            resp = conn.getresponse()
            resp.read()
            assert resp.status == 204
        finally:
            conn.close()

    def test_options_has_cors_headers(self, live_server):
        """Test that OPTIONS response includes CORS headers."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server.port, timeout=10)
        try:
            conn.request("OPTIONS", "/api/status", headers={"Origin": "http://localhost:8787"})
            resp = conn.getresponse()
            resp.read()
            assert "GET, POST, OPTIONS" in resp.getheader("Access-Control-Allow-Methods", "")
            assert "Content-Type" in resp.getheader("Access-Control-Allow-Headers", "")
            assert resp.getheader("Access-Control-Allow-Origin") == "http://localhost:8787"
        finally:
            conn.close()

    def test_options_on_any_path(self, live_server):
        """Test that OPTIONS works on any API path."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server.port, timeout=10)
        try:
            conn.request("OPTIONS", "/api/chat")
            resp = conn.getresponse()
            resp.read()
            assert resp.status == 204
        finally:
            conn.close()


# ── Ollama Edge Cases ───────────────────────────────────────────────


@pytest.mark.unit
class TestOllamaEdgeCases:
    """Tests for Ollama error paths — skipped when Ollama is running."""

    def test_chat_timeout_returns_error(self, live_server):
        """Test that when Ollama is unreachable, chat returns an error code."""
        if _OLLAMA_AVAILABLE:
            pytest.skip("Ollama is running — cannot test timeout path")
        status, data = live_server.post("/api/chat", {"message": "Hello"})
        assert status in (503, 504)
        assert "error" in data

    def test_awareness_timeout_returns_error(self, live_server):
        """Test that when Ollama is unreachable, awareness returns error."""
        if _OLLAMA_AVAILABLE:
            pytest.skip("Ollama is running — cannot test timeout path")
        status, data = live_server.post(
            "/api/awareness/summary", {"model": "llama3"}
        )
        assert status in (503, 504)
        assert "error" in data


# ── JSON Response Headers Tests ─────────────────────────────────────


@pytest.mark.unit
class TestResponseHeaders:
    """Tests verifying CORS headers are present on JSON responses."""

    def test_json_response_has_cors_headers(self, live_server):
        """Test that JSON API responses include proper CORS headers."""
        import http.client
        # The default _LiveServer origin injection uses 127.0.0.1,
        # but the server may reflect or normalize. We verify it sets one.
        conn = http.client.HTTPConnection("127.0.0.1", live_server.port, timeout=10)
        try:
            conn.request("GET", "/api/status", headers={"Origin": "http://127.0.0.1:8787"})
            resp = conn.getresponse()
            resp.read()
            origin = resp.getheader("Access-Control-Allow-Origin")
            assert origin in ("http://127.0.0.1:8787", "http://localhost:8787", "*")
            assert "GET, POST, OPTIONS" in resp.getheader("Access-Control-Allow-Methods", "")
            if getattr(resp, "getheader", lambda k, d="": "")("Access-Control-Allow-Headers"):
                assert "Content-Type" in resp.getheader("Access-Control-Allow-Headers", "")
            # The content type returned by live_server for /api/status is json
            assert "application/json" in resp.getheader("Content-Type", "")
        finally:
            conn.close()

    def test_error_response_has_cors_headers(self, live_server):
        """Test that JSON error responses also include CORS headers."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server.port, timeout=10)
        try:
            # Config get with a traversal attack path — returns JSON error with CORS headers
            conn.request("GET", "/api/config/%2F..%2Fetc%2Fpasswd",
                        headers={"Origin": "http://localhost:8787"})
            resp = conn.getresponse()
            resp.read()
            # JSON error responses via send_json_response include CORS headers
            assert resp.getheader("Access-Control-Allow-Origin") == "http://localhost:8787"
        finally:
            conn.close()


# ── Trust Status Endpoint Tests ──────────────────────────────────────


@pytest.mark.unit
class TestTrustStatusEndpoint:
    """Tests for GET /api/trust/status."""

    def test_returns_200(self, live_server):
        """GET /api/trust/status returns HTTP 200."""
        status, data = live_server.get("/api/trust/status")
        assert status == 200

    def test_response_has_counts_dict_with_required_keys(self, live_server):
        """Response includes counts dict with untrusted/verified/trusted keys >= 0."""
        status, data = live_server.get("/api/trust/status")
        assert status == 200
        assert isinstance(data, dict)
        assert "counts" in data
        counts = data["counts"]
        for key in ("untrusted", "verified", "trusted"):
            assert key in counts
            assert isinstance(counts[key], int)
            assert counts[key] >= 0

    def test_response_has_total_tools_int(self, live_server):
        """Response includes total_tools as a non-negative integer."""
        status, data = live_server.get("/api/trust/status")
        assert status == 200
        assert "total_tools" in data
        assert isinstance(data["total_tools"], int)
        assert data["total_tools"] >= 0


# ── PAI Action Endpoint Tests ────────────────────────────────────────


@pytest.mark.unit
class TestPaiActionEndpoint:
    """Tests for POST /api/pai/action."""

    def test_empty_action_returns_400(self, live_server):
        """POST with empty action string returns 400 with success=False."""
        status, data = live_server.post("/api/pai/action", {})
        assert status == 400
        assert isinstance(data, dict)
        assert data.get("success") is False

    def test_unknown_action_returns_400(self, live_server):
        """POST with unrecognised action returns 400 with success=False."""
        status, data = live_server.post("/api/pai/action", {"action": "foobar"})
        assert status == 400
        assert data.get("success") is False

    def test_verify_action_returns_correct_shape(self, live_server):
        """verify action returns 200 with integer modules/tools_total/promoted."""
        status, data = live_server.post("/api/pai/action", {"action": "verify"})
        assert status == 200
        assert data.get("success") is True
        result = data.get("result", {})
        assert isinstance(result.get("modules"), int)
        assert isinstance(result.get("tools_total"), int)
        assert isinstance(result.get("promoted"), int)
        assert "trust_counts" in data

    def test_trust_action_returns_200(self, live_server):
        """trust action returns 200 with success=True."""
        status, data = live_server.post("/api/pai/action", {"action": "trust"})
        assert status == 200
        assert data.get("success") is True

    def test_reset_action_returns_200_with_reset_message(self, live_server):
        """reset action returns 200 and result message contains 'reset'."""
        status, data = live_server.post("/api/pai/action", {"action": "reset"})
        assert status == 200
        assert data.get("success") is True
        result = data.get("result", {})
        assert "reset" in str(result.get("message", "")).lower()

    def test_status_action_returns_200(self, live_server):
        """status action returns 200 with success=True."""
        status, data = live_server.post("/api/pai/action", {"action": "status"})
        assert status == 200
        assert data.get("success") is True

    def test_add_memory_empty_content_returns_400(self, live_server):
        """add_memory with empty content returns 400 with success=False."""
        status, data = live_server.post(
            "/api/pai/action", {"action": "add_memory", "content": ""}
        )
        assert status == 400
        assert data.get("success") is False

    @_skip_no_agentic_memory
    def test_add_memory_with_content_returns_200(self, live_server):
        """add_memory with non-empty content returns 200 with success=True."""
        status, data = live_server.post(
            "/api/pai/action", {"action": "add_memory", "content": "test note"}
        )
        assert status == 200
        assert data.get("success") is True


# ── PAI Action New Backends Tests ────────────────────────────────────


@pytest.mark.unit
class TestPaiActionNewBackends:
    """Tests for the analyze, search, and docs PAI actions."""

    def test_analyze_action_returns_200(self, live_server):
        """analyze action returns 200 with success=True."""
        status, data = live_server.post("/api/pai/action", {"action": "analyze"})
        assert status == 200
        assert data.get("success") is True

    def test_analyze_result_has_module_counts(self, live_server):
        """analyze result includes total_modules and active_modules."""
        status, data = live_server.post("/api/pai/action", {"action": "analyze"})
        assert status == 200
        result = data.get("result", {})
        assert "total_modules" in result
        assert "active_modules" in result
        assert isinstance(result["total_modules"], int)
        assert isinstance(result["active_modules"], int)

    def test_search_without_query_returns_400(self, live_server):
        """search action without 'query' field returns 400 with success=False."""
        status, data = live_server.post("/api/pai/action", {"action": "search"})
        assert status == 400
        assert data.get("success") is False

    def test_search_with_query_returns_200(self, live_server):
        """search with a valid query returns 200 and hits list."""
        status, data = live_server.post("/api/pai/action", {"action": "search", "query": "fake"})
        assert status == 200
        assert data.get("success") is True
        result = data.get("result", {})
        assert "hits" in result
        assert "count" in result
        assert isinstance(result["hits"], list)
        assert isinstance(result["count"], int)

    def test_search_invalid_regex_returns_400(self, live_server):
        """search with an invalid regex pattern returns 400 with success=False."""
        status, data = live_server.post("/api/pai/action", {"action": "search", "query": "[invalid"})
        assert status == 400
        assert data.get("success") is False

    def test_docs_without_module_returns_400(self, live_server):
        """docs action without 'module' field returns 400 with success=False."""
        status, data = live_server.post("/api/pai/action", {"action": "docs"})
        assert status == 400
        assert data.get("success") is False

    def test_docs_unknown_module_returns_404(self, live_server):
        """docs action with non-existent module returns 404 with success=False."""
        status, data = live_server.post("/api/pai/action", {"action": "docs", "module": "nonexistent_module_xyz"})
        assert status == 404
        assert data.get("success") is False

    def test_docs_known_module_returns_200(self, live_server):
        """docs action with the live server's fake_mod returns 200 and a result dict."""
        status, data = live_server.post("/api/pai/action", {"action": "docs", "module": "fake_mod"})
        assert status == 200
        assert data.get("success") is True
        result = data.get("result", {})
        assert isinstance(result, dict)


# ── Agent Dispatch Status Endpoint Tests ─────────────────────────────


@pytest.mark.unit
class TestAgentDispatchStatusEndpoint:
    """Tests for GET /api/agent/dispatch/status."""

    def test_returns_200(self, live_server):
        """GET /api/agent/dispatch/status returns HTTP 200."""
        WebsiteServer._dispatch_orch = None
        status, data = live_server.get("/api/agent/dispatch/status")
        assert status == 200

    def test_active_is_false_when_no_orch(self, live_server):
        """active=False when no orchestrator has been started."""
        WebsiteServer._dispatch_orch = None
        status, data = live_server.get("/api/agent/dispatch/status")
        assert status == 200
        assert data.get("active") is False

    def test_turns_list_always_present(self, live_server):
        """Response always includes a turns list even when inactive."""
        WebsiteServer._dispatch_orch = None
        status, data = live_server.get("/api/agent/dispatch/status")
        assert status == 200
        assert "turns" in data
        assert isinstance(data["turns"], list)


# ── Agent Dispatch Endpoint Tests ────────────────────────────────────


@pytest.mark.unit
class TestAgentDispatchEndpoint:
    """Tests for POST /api/agent/dispatch."""

    def test_empty_body_returns_400(self, live_server):
        """POST with Content-Length 0 returns 400."""
        conn = http.client.HTTPConnection("127.0.0.1", live_server.port, timeout=10)
        try:
            conn.request(
                "POST",
                "/api/agent/dispatch",
                body=b"",
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": "0",
                    "Origin": "http://127.0.0.1:8787",
                },
            )
            resp = conn.getresponse()
            resp.read()
            assert resp.status == 400
        finally:
            conn.close()

    def test_with_prompt_returns_dict(self, live_server):
        """POST with a prompt returns a dict response (200 or 500 if orch unavailable)."""
        WebsiteServer._dispatch_orch = None
        WebsiteServer._dispatch_thread = None
        status, data = live_server.post("/api/agent/dispatch", {"prompt": "hello"})
        assert status in (200, 500)
        assert isinstance(data, dict)
        if status == 200:
            assert data.get("success") is True
            assert "channel" in data

    def test_running_thread_returns_429(self, live_server):
        """Already-running dispatch thread returns 429."""
        # Create a live thread using an event to control its lifetime
        stop_event = threading.Event()

        def _keep_alive():
            stop_event.wait(timeout=10)

        t = threading.Thread(target=_keep_alive, daemon=True)
        t.start()
        try:
            WebsiteServer._dispatch_thread = t
            status, data = live_server.post("/api/agent/dispatch", {"prompt": "hello"})
            assert status == 429
        finally:
            stop_event.set()
            t.join(timeout=2)
            WebsiteServer._dispatch_thread = None


# ── Agent Dispatch Stop Endpoint Tests ───────────────────────────────


@pytest.mark.unit
class TestAgentDispatchStopEndpoint:
    """Tests for POST /api/agent/dispatch/stop."""

    def test_no_active_dispatch_returns_200(self, live_server):
        """POST when no dispatch is active returns 200 with success=True."""
        WebsiteServer._dispatch_orch = None
        status, data = live_server.post("/api/agent/dispatch/stop", {})
        assert status == 200
        assert data.get("success") is True

    def test_stop_clears_orch(self, live_server):
        """POST stop clears WebsiteServer._dispatch_orch to None."""

        class _DummyOrch:
            pass

        WebsiteServer._dispatch_orch = _DummyOrch()
        status, data = live_server.post("/api/agent/dispatch/stop", {})
        assert status == 200
        assert data.get("success") is True
        assert WebsiteServer._dispatch_orch is None

    def test_response_always_has_message_field(self, live_server):
        """Response always includes a message field."""
        WebsiteServer._dispatch_orch = None
        status, data = live_server.post("/api/agent/dispatch/stop", {})
        assert status == 200
        assert "message" in data


# ── Telemetry Endpoint Tests ──────────────────────────────────────────


@pytest.mark.unit
class TestTelemetryEndpoint:
    """Tests for GET /api/telemetry."""

    def test_returns_200(self, live_server):
        """GET /api/telemetry returns HTTP 200."""
        status, data = live_server.get("/api/telemetry")
        assert status == 200

    def test_response_has_status_field(self, live_server):
        """Response is a dict with a status field."""
        status, data = live_server.get("/api/telemetry")
        assert status == 200
        assert isinstance(data, dict)
        assert "status" in data

    def test_response_has_metric_names_list(self, live_server):
        """Response includes metric_names as a list."""
        status, data = live_server.get("/api/telemetry")
        assert status == 200
        assert "metric_names" in data
        assert isinstance(data["metric_names"], list)

    def test_response_has_dashboards_list(self, live_server):
        """Response includes dashboards as a list."""
        status, data = live_server.get("/api/telemetry")
        assert status == 200
        assert "dashboards" in data
        assert isinstance(data["dashboards"], list)

    def test_response_has_total_metrics_int(self, live_server):
        """Response includes total_metrics as a non-negative integer."""
        status, data = live_server.get("/api/telemetry")
        assert status == 200
        assert "total_metrics" in data
        assert isinstance(data["total_metrics"], int)
        assert data["total_metrics"] >= 0


# ── Security Posture Endpoint Tests ──────────────────────────────────


@pytest.mark.unit
class TestSecurityPostureEndpoint:
    """Tests for GET /api/security/posture."""

    def test_returns_200(self, live_server):
        """GET /api/security/posture returns HTTP 200."""
        status, data = live_server.get("/api/security/posture")
        assert status == 200

    def test_response_has_status_field(self, live_server):
        """Response is a dict with a status field."""
        status, data = live_server.get("/api/security/posture")
        assert status == 200
        assert isinstance(data, dict)
        assert "status" in data

    def test_risk_score_in_range_when_ok(self, live_server):
        """risk_score is 0–100 when status is ok."""
        status, data = live_server.get("/api/security/posture")
        assert status == 200
        if data.get("status") == "ok":
            assert "risk_score" in data
            assert isinstance(data["risk_score"], (int, float))
            assert 0 <= data["risk_score"] <= 100

    def test_compliance_rate_present_when_ok(self, live_server):
        """compliance_rate present when status is ok."""
        status, data = live_server.get("/api/security/posture")
        assert status == 200
        if data.get("status") == "ok":
            assert "compliance_rate" in data
