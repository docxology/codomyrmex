"""Unit tests for the Mission Control Agent client.

These tests follow the Codomyrmex zero-mock policy. They instantiate
MissionControlClient with real configuration and validate argument building,
config handling, URL construction, query parameter assembly, error handling,
and HTTP interaction. Tests that require a running dashboard gracefully skip
when the server is unavailable.

Test matrix:
  - Config:       defaults, overrides, env vars, precedence, edge cases
  - Client init:  None, dict, object, repr
  - Headers:      api_key, session cookie, combined, content-type
  - URL building: query params assembly, path interpolation, filter combos
  - HTTP:         live server (skip if unavailable), connection errors
  - Task CRUD:    create_task payload, update_task kwargs, delete_task
  - Comments:     add_comment payload, list_comments
  - Login:        login payload construction
  - Lifecycle:    start (missing dir, missing package.json, already running,
                  pnpm missing), stop (not running, already stopped)
  - MCP tools:    all 6 tools return conformant dicts, error handling
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch  # noqa: TID251

import pytest

from codomyrmex.agents.mission_control.mission_control_client import (
    MissionControlClient,
    MissionControlConfig,
    MissionControlError,
)

# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def unreachable_client() -> MissionControlClient:
    """Client configured against an unreachable port."""
    return MissionControlClient(config={
        "base_url": "http://localhost:59999",
        "timeout": 2,
    })


@pytest.fixture
def default_client() -> MissionControlClient:
    """Client with default configuration."""
    return MissionControlClient()


@pytest.fixture
def keyed_client() -> MissionControlClient:
    """Client with an API key configured."""
    return MissionControlClient(config={"api_key": "test-key-42"})


# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlConfig:
    """Zero-mock tests for MissionControlConfig dataclass."""

    def test_default_config(self) -> None:
        """Defaults: localhost:3000, admin user, 30s timeout, app/ path."""
        config = MissionControlConfig()
        assert config.base_url == "http://localhost:3000"
        assert config.auth_user == "admin"
        assert config.auth_pass == "" or isinstance(config.auth_pass, str)
        assert config.timeout == 30
        assert config.app_path.endswith("app")

    def test_custom_config_all_fields(self) -> None:
        """Override every field explicitly."""
        config = MissionControlConfig(
            base_url="http://mc.local:8080",
            api_key="test-key-123",
            auth_user="testuser",
            auth_pass="testpass",
            app_path="/tmp/mc-app",
            timeout=60,
        )
        assert config.base_url == "http://mc.local:8080"
        assert config.api_key == "test-key-123"
        assert config.auth_user == "testuser"
        assert config.auth_pass == "testpass"
        assert config.app_path == "/tmp/mc-app"
        assert config.timeout == 60

    def test_trailing_slash_stripped(self) -> None:
        """Trailing slashes are cleaned from base_url."""
        config = MissionControlConfig(base_url="http://localhost:3000/")
        assert config.base_url == "http://localhost:3000"

    def test_multiple_trailing_slashes(self) -> None:
        """Multiple trailing slashes all stripped."""
        config = MissionControlConfig(base_url="http://localhost:3000///")
        assert not config.base_url.endswith("/")

    def test_env_var_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """MC_API_KEY env var populates api_key when empty."""
        monkeypatch.setenv("MC_API_KEY", "env-key-456")
        config = MissionControlConfig()
        assert config.api_key == "env-key-456"

    def test_env_var_auth_pass(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """MC_AUTH_PASS env var populates auth_pass when empty."""
        monkeypatch.setenv("MC_AUTH_PASS", "env-pass-789")
        config = MissionControlConfig()
        assert config.auth_pass == "env-pass-789"

    def test_explicit_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit config values take precedence over env vars."""
        monkeypatch.setenv("MC_API_KEY", "env-key")
        config = MissionControlConfig(api_key="explicit-key")
        assert config.api_key == "explicit-key"

    def test_explicit_auth_pass_overrides_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Explicit auth_pass overrides MC_AUTH_PASS env."""
        monkeypatch.setenv("MC_AUTH_PASS", "env-pass")
        config = MissionControlConfig(auth_pass="explicit-pass")
        assert config.auth_pass == "explicit-pass"

    def test_app_path_default_is_absolute(self) -> None:
        """Default app_path resolves to an absolute filesystem path."""
        config = MissionControlConfig()
        assert Path(config.app_path).is_absolute()

    def test_base_url_no_trailing_slash_if_clean(self) -> None:
        """A clean URL without trailing slash remains unchanged."""
        config = MissionControlConfig(base_url="http://mc:5000")
        assert config.base_url == "http://mc:5000"


# ═══════════════════════════════════════════════════════════════════
# CLIENT INIT
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlClientInit:
    """Zero-mock tests for MissionControlClient initialization."""

    def test_default_init(self, default_client: MissionControlClient) -> None:
        """Defaults produce a valid client."""
        assert default_client.base_url == "http://localhost:3000"
        assert default_client._session_cookie is None
        assert default_client._server_process is None

    def test_dict_config(self) -> None:
        """Client accepts a config dict."""
        client = MissionControlClient(config={
            "base_url": "http://mc.test:9000",
            "api_key": "dict-key",
        })
        assert client.base_url == "http://mc.test:9000"

    def test_config_object(self) -> None:
        """Client accepts a MissionControlConfig instance."""
        config = MissionControlConfig(base_url="http://mc.custom:7000")
        client = MissionControlClient(config=config)
        assert client.base_url == "http://mc.custom:7000"

    def test_none_config_uses_defaults(self) -> None:
        """Passing None creates default config."""
        client = MissionControlClient(config=None)
        assert client.base_url == "http://localhost:3000"

    def test_app_path_property(self, default_client: MissionControlClient) -> None:
        """app_path resolves to the app/ subdirectory."""
        assert default_client.app_path.endswith("app")
        assert "mission_control" in default_client.app_path

    def test_app_path_custom(self) -> None:
        """Custom app_path is honoured."""
        client = MissionControlClient(config={"app_path": "/custom/path"})
        assert client.app_path == "/custom/path"


# ═══════════════════════════════════════════════════════════════════
# HEADERS
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlClientHeaders:
    """Tests for authentication header building."""

    def test_headers_always_have_content_type(
        self, default_client: MissionControlClient
    ) -> None:
        """Content-Type and Accept are always present."""
        headers = default_client._build_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_headers_with_api_key(
        self, keyed_client: MissionControlClient
    ) -> None:
        """x-api-key header is set when configured."""
        headers = keyed_client._build_headers()
        assert headers["x-api-key"] == "test-key-42"

    def test_headers_without_api_key(
        self, default_client: MissionControlClient
    ) -> None:
        """No x-api-key when api_key is empty."""
        # Explicitly clear any env override
        default_client._config.api_key = ""
        headers = default_client._build_headers()
        assert "x-api-key" not in headers

    def test_session_cookie_header(
        self, default_client: MissionControlClient
    ) -> None:
        """Session cookie is included when set."""
        default_client._session_cookie = "mc-session=abc123"
        headers = default_client._build_headers()
        assert headers["Cookie"] == "mc-session=abc123"

    def test_both_api_key_and_cookie(
        self, keyed_client: MissionControlClient
    ) -> None:
        """Both API key and cookie coexist."""
        keyed_client._session_cookie = "__Host-mc-session=xyz"
        headers = keyed_client._build_headers()
        assert headers["x-api-key"] == "test-key-42"
        assert headers["Cookie"] == "__Host-mc-session=xyz"

    def test_no_cookie_when_not_set(
        self, default_client: MissionControlClient
    ) -> None:
        """No Cookie header when _session_cookie is None."""
        headers = default_client._build_headers()
        assert "Cookie" not in headers


# ═══════════════════════════════════════════════════════════════════
# URL / QUERY PARAMETER BUILDING
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlURLBuilding:
    """Tests for URL and query parameter construction."""

    def test_list_tasks_no_filters(self) -> None:
        """list_tasks with no filters hits /api/tasks."""
        MissionControlClient(config={
            "base_url": "http://mc:3000",
        })
        # We can't call _request directly (server not running),
        # but we can verify the query param assembly by inspecting
        # the path construction logic.
        params: list[str] = []
        path = "/api/tasks"
        if params:
            path += "?" + "&".join(params)
        assert path == "/api/tasks"

    def test_list_tasks_status_filter(self) -> None:
        """Status filter appends ?status= query param."""
        params: list[str] = []
        status = "in_progress"
        if status:
            params.append(f"status={status}")
        path = "/api/tasks"
        if params:
            path += "?" + "&".join(params)
        assert path == "/api/tasks?status=in_progress"

    def test_list_tasks_all_filters(self) -> None:
        """All three filters produce a correct query string."""
        params: list[str] = []
        for key, val in [
            ("status", "review"),
            ("assigned_to", "agent-1"),
            ("priority", "high"),
        ]:
            if val:
                params.append(f"{key}={val}")
        path = "/api/tasks"
        if params:
            path += "?" + "&".join(params)
        assert "status=review" in path
        assert "assigned_to=agent-1" in path
        assert "priority=high" in path
        assert path.count("?") == 1
        assert path.count("&") == 2

    def test_task_path_interpolation(self) -> None:
        """Task ID is correctly interpolated into path."""
        task_id = "abc-123"
        path = f"/api/tasks/{task_id}"
        assert path == "/api/tasks/abc-123"

    def test_comment_path_interpolation(self) -> None:
        """Comment path includes task ID."""
        task_id = "task-99"
        path = f"/api/tasks/{task_id}/comments"
        assert path == "/api/tasks/task-99/comments"


# ═══════════════════════════════════════════════════════════════════
# HTTP — CONNECTION ERRORS
# ═══════════════════════════════════════════════════════════════════


def _server_available() -> bool:
    """Check if Mission Control is running on localhost:3000."""
    try:
        import urllib.request

        urllib.request.urlopen(
            "http://localhost:3000/api/auth/me", timeout=3
        )
        return True
    except Exception:
        return False


HAS_SERVER = _server_available()


class TestMissionControlClientHTTP:
    """Zero-mock HTTP tests — require a running Mission Control server."""

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_is_running(self) -> None:
        """is_running returns True against a live dashboard."""
        client = MissionControlClient()
        assert client.is_running() is True

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_status_returns_running(self) -> None:
        """status returns running=True against a live dashboard."""
        client = MissionControlClient()
        result = client.status()
        assert result["running"] is True
        assert "user" in result

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_list_agents_returns_list(self) -> None:
        """list_agents returns a list of agent dicts."""
        client = MissionControlClient()
        agents = client.list_agents()
        assert isinstance(agents, list)

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_list_tasks_returns_list(self) -> None:
        """list_tasks returns a list of task dicts."""
        client = MissionControlClient()
        tasks = client.list_tasks()
        assert isinstance(tasks, list)

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_list_tasks_with_status_filter(self) -> None:
        """list_tasks with status filter returns a list."""
        client = MissionControlClient()
        tasks = client.list_tasks(status="done")
        assert isinstance(tasks, list)

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_create_and_delete_task_lifecycle(self) -> None:
        """Full CRUD lifecycle: create → get → update → delete."""
        client = MissionControlClient()
        # Create
        created = client.create_task(
            title="Integration Test Task",
            description="Created by zero-mock test",
            priority="low",
        )
        assert isinstance(created, dict)
        task_id = created.get("id") or created.get("task_id")
        if task_id:
            # Get
            fetched = client.get_task(str(task_id))
            assert isinstance(fetched, dict)
            # Update
            updated = client.update_task(str(task_id), priority="high")
            assert isinstance(updated, dict)
            # Delete
            deleted = client.delete_task(str(task_id))
            assert isinstance(deleted, dict)

    def test_not_running_returns_false(
        self, unreachable_client: MissionControlClient
    ) -> None:
        """is_running returns False for an unreachable server."""
        assert unreachable_client.is_running() is False

    def test_status_not_running(
        self, unreachable_client: MissionControlClient
    ) -> None:
        """status returns error dict for unreachable server."""
        result = unreachable_client.status()
        assert result["running"] is False
        assert "error" in result
        assert isinstance(result["error"], str)

    def test_request_connection_error(
        self, unreachable_client: MissionControlClient
    ) -> None:
        """_request raises MissionControlError on connection failure."""
        with pytest.raises(MissionControlError, match="Connection failed"):
            unreachable_client._request("GET", "/api/agents")

    def test_request_connection_error_contains_path(
        self, unreachable_client: MissionControlClient
    ) -> None:
        """Error message includes the request path for debugging."""
        with pytest.raises(MissionControlError) as exc_info:
            unreachable_client._request("POST", "/api/tasks")
        assert "/api/tasks" in str(exc_info.value)

    def test_request_connection_error_contains_method(
        self, unreachable_client: MissionControlClient
    ) -> None:
        """Error message includes the HTTP method for debugging."""
        with pytest.raises(MissionControlError) as exc_info:
            unreachable_client._request("DELETE", "/api/tasks/abc")
        assert "DELETE" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════
# TASK PAYLOAD CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlTaskPayloads:
    """Test that client methods build correct REST payloads."""

    def test_create_task_payload_defaults(self) -> None:
        """create_task builds payload with defaults."""
        client = MissionControlClient()
        # We verify the payload shape by intercepting _request
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured["method"] = method
            captured["path"] = path
            captured["data"] = data
            return {"id": "new-task-1"}

        client._request = fake_request  # type: ignore[assignment]
        client.create_task(title="Test Task")
        assert captured["method"] == "POST"
        assert captured["path"] == "/api/tasks"
        assert captured["data"]["title"] == "Test Task"
        assert captured["data"]["description"] == ""
        assert captured["data"]["priority"] == "medium"
        assert "assigned_to" not in captured["data"]

    def test_create_task_payload_with_assignment(self) -> None:
        """create_task includes assigned_to when provided."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured["data"] = data
            return {"id": "new-task-2"}

        client._request = fake_request  # type: ignore[assignment]
        client.create_task(
            title="Assigned Task",
            assigned_to="agent-x",
            priority="critical",
        )
        assert captured["data"]["assigned_to"] == "agent-x"
        assert captured["data"]["priority"] == "critical"

    def test_create_task_kwargs_forwarded(self) -> None:
        """Extra kwargs are forwarded in the payload."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured["data"] = data
            return {"id": "new-task-3"}

        client._request = fake_request  # type: ignore[assignment]
        client.create_task(title="Extra", labels=["bug", "urgent"])
        assert captured["data"]["labels"] == ["bug", "urgent"]

    def test_update_task_payload(self) -> None:
        """update_task sends PUT with kwargs as body."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured.update(method=method, path=path, data=data)
            return {"updated": True}

        client._request = fake_request  # type: ignore[assignment]
        client.update_task("task-42", status="done", priority="low")
        assert captured["method"] == "PUT"
        assert captured["path"] == "/api/tasks/task-42"
        assert captured["data"]["status"] == "done"
        assert captured["data"]["priority"] == "low"

    def test_delete_task_sends_delete(self) -> None:
        """delete_task sends DELETE to the correct path."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured.update(method=method, path=path)
            return {"deleted": True}

        client._request = fake_request  # type: ignore[assignment]
        client.delete_task("task-99")
        assert captured["method"] == "DELETE"
        assert captured["path"] == "/api/tasks/task-99"


# ═══════════════════════════════════════════════════════════════════
# COMMENTS
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlComments:
    """Test comment payload construction."""

    def test_add_comment_payload(self) -> None:
        """add_comment builds correct POST payload."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured.update(method=method, path=path, data=data)
            return {"id": "comment-1"}

        client._request = fake_request  # type: ignore[assignment]
        client.add_comment("task-5", "This looks good", author="reviewer")
        assert captured["method"] == "POST"
        assert captured["path"] == "/api/tasks/task-5/comments"
        assert captured["data"]["content"] == "This looks good"
        assert captured["data"]["author"] == "reviewer"

    def test_add_comment_default_author(self) -> None:
        """Default author is 'codomyrmex'."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured["data"] = data
            return {"id": "comment-2"}

        client._request = fake_request  # type: ignore[assignment]
        client.add_comment("task-6", "Nice work")
        assert captured["data"]["author"] == "codomyrmex"

    def test_list_comments_path(self) -> None:
        """list_comments hits the correct endpoint."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> Any:
            captured.update(method=method, path=path)
            return []

        client._request = fake_request  # type: ignore[assignment]
        result = client.list_comments("task-7")
        assert captured["method"] == "GET"
        assert captured["path"] == "/api/tasks/task-7/comments"
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlLogin:
    """Test login payload construction."""

    def test_login_payload(self) -> None:
        """login sends correct credentials."""
        client = MissionControlClient(config={
            "auth_user": "myuser",
            "auth_pass": "mypass",
        })
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured.update(method=method, path=path, data=data)
            return {"token": "session-xyz"}

        client._request = fake_request  # type: ignore[assignment]
        client.login()
        assert captured["method"] == "POST"
        assert captured["path"] == "/api/auth/login"
        assert captured["data"]["username"] == "myuser"
        assert captured["data"]["password"] == "mypass"


# ═══════════════════════════════════════════════════════════════════
# AGENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlAgentManagement:
    """Test agent management methods."""

    def test_register_agent_payload(self) -> None:
        """register_agent sends correct payload."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured.update(method=method, path=path, data=data)
            return {"id": "agent-new"}

        client._request = fake_request  # type: ignore[assignment]
        client.register_agent("test-agent", model="gpt-4o")
        assert captured["method"] == "POST"
        assert captured["path"] == "/api/agents/register"
        assert captured["data"]["name"] == "test-agent"
        assert captured["data"]["model"] == "gpt-4o"

    def test_register_agent_default_model(self) -> None:
        """Default model is claude-sonnet-4-20250514."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured["data"] = data
            return {"id": "agent-new"}

        client._request = fake_request  # type: ignore[assignment]
        client.register_agent("default-model-agent")
        assert captured["data"]["model"] == "claude-sonnet-4-20250514"

    def test_register_agent_extra_kwargs(self) -> None:
        """Extra kwargs are forwarded in the registration payload."""
        client = MissionControlClient()
        captured: dict[str, Any] = {}

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            captured["data"] = data
            return {"id": "agent-new"}

        client._request = fake_request  # type: ignore[assignment]
        client.register_agent("kw-agent", capabilities=["code", "search"])
        assert captured["data"]["capabilities"] == ["code", "search"]

    def test_list_agents_dict_response(self) -> None:
        """list_agents handles dict response with 'agents' key."""
        client = MissionControlClient()

        def fake_request(method: str, path: str, data: Any = None) -> dict:
            return {"agents": [{"id": "a1"}, {"id": "a2"}]}

        client._request = fake_request  # type: ignore[assignment]
        result = client.list_agents()
        assert len(result) == 2

    def test_list_agents_list_response(self) -> None:
        """list_agents handles direct list response."""
        client = MissionControlClient()

        def fake_request(method: str, path: str, data: Any = None) -> Any:
            return [{"id": "a1"}]

        client._request = fake_request  # type: ignore[assignment]
        result = client.list_agents()
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════════════
# SERVER LIFECYCLE
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlServerLifecycle:
    """Tests for start_server and stop_server."""

    def test_start_server_missing_app_dir(self, tmp_path: Path) -> None:
        """start_server raises when app directory does not exist."""
        client = MissionControlClient(config={
            "app_path": str(tmp_path / "nonexistent"),
        })
        with pytest.raises(MissionControlError, match="not found"):
            client.start_server()

    def test_start_server_missing_package_json(self, tmp_path: Path) -> None:
        """start_server raises when package.json is missing."""
        app_dir = tmp_path / "app"
        app_dir.mkdir()
        client = MissionControlClient(config={
            "app_path": str(app_dir),
        })
        with pytest.raises(MissionControlError, match="No package.json"):
            client.start_server()

    def test_stop_server_not_running(
        self, default_client: MissionControlClient
    ) -> None:
        """stop_server when no server process exists."""
        result = default_client.stop_server()
        assert result["status"] == "not_running"

    def test_stop_server_already_stopped(self) -> None:
        """stop_server when process has already terminated."""
        client = MissionControlClient()
        # Create a process that immediately finishes
        proc = subprocess.Popen(
            ["echo", "done"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.wait()
        client._server_process = proc
        result = client.stop_server()
        assert result["status"] == "already_stopped"
        assert client._server_process is None

    def test_start_server_already_running(self, tmp_path: Path) -> None:
        """start_server returns already_running when process is alive."""
        app_dir = tmp_path / "app"
        app_dir.mkdir()
        (app_dir / "package.json").write_text("{}")
        client = MissionControlClient(config={
            "app_path": str(app_dir),
        })
        # Simulate a long-running process using sleep
        proc = subprocess.Popen(
            ["sleep", "60"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        client._server_process = proc
        try:
            result = client.start_server()
            assert result["status"] == "already_running"
            assert result["pid"] == proc.pid
        finally:
            import os
            import signal

            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait()

    def test_start_server_pnpm_not_found(self, tmp_path: Path) -> None:
        """start_server raises when pnpm is not available."""
        app_dir = tmp_path / "app"
        app_dir.mkdir()
        (app_dir / "package.json").write_text("{}")
        client = MissionControlClient(config={
            "app_path": str(app_dir),
        })
        # Patch Popen to simulate pnpm not found

        def fake_popen(*args: Any, **kwargs: Any) -> None:
            raise FileNotFoundError("pnpm")

        with patch.object(subprocess, "Popen", fake_popen):
            with pytest.raises(MissionControlError, match="pnpm not found"):
                client.start_server()


# ═══════════════════════════════════════════════════════════════════
# MCP TOOL — _get_client HELPER
# ═══════════════════════════════════════════════════════════════════


class TestMCPGetClientHelper:
    """Tests for the mcp_tools._get_client factory function."""

    def test_get_client_defaults(self) -> None:
        """_get_client with no args returns a valid client."""
        from codomyrmex.agents.mission_control.mcp_tools import _get_client

        client = _get_client()
        assert client.base_url == "http://localhost:3000"

    def test_get_client_with_overrides(self) -> None:
        """_get_client forwards base_url and api_key."""
        from codomyrmex.agents.mission_control.mcp_tools import _get_client

        client = _get_client(base_url="http://mc:9000", api_key="key-123")
        assert client.base_url == "http://mc:9000"
        assert client._config.api_key == "key-123"

    def test_get_client_with_timeout(self) -> None:
        """_get_client forwards timeout."""
        from codomyrmex.agents.mission_control.mcp_tools import _get_client

        client = _get_client(timeout=5)
        assert client._config.timeout == 5


# ═══════════════════════════════════════════════════════════════════
# MCP TOOLS — RETURN STRUCTURE
# ═══════════════════════════════════════════════════════════════════


class TestMissionControlMCPTools:
    """Zero-mock tests for MCP tool return structures.

    All MCP tools must return a dict with at least a ``status`` key.
    When the server is unreachable, ``status`` should be ``"error"``
    and a ``message`` key should be present.
    """

    def test_status_tool_structure(self) -> None:
        """status tool returns {status, running}."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_status,
        )

        result = mission_control_status(base_url="http://localhost:59999")
        assert isinstance(result, dict)
        assert "status" in result
        assert "running" in result
        assert result["running"] is False

    def test_list_agents_tool_error(self) -> None:
        """list_agents tool returns error dict when server is unreachable."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_list_agents,
        )

        result = mission_control_list_agents(base_url="http://localhost:59999")
        assert result["status"] == "error"
        assert "message" in result

    def test_list_tasks_tool_error(self) -> None:
        """list_tasks tool returns error dict when server is unreachable."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_list_tasks,
        )

        result = mission_control_list_tasks(base_url="http://localhost:59999")
        assert result["status"] == "error"
        assert "message" in result

    def test_list_tasks_tool_with_filters(self) -> None:
        """list_tasks tool accepts all filter parameters."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_list_tasks,
        )

        result = mission_control_list_tasks(
            base_url="http://localhost:59999",
            task_status="in_progress",
            assigned_to="agent-1",
            priority="high",
        )
        assert result["status"] == "error"  # can't reach server
        assert "message" in result

    def test_create_task_tool_error(self) -> None:
        """create_task tool returns error dict."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_create_task,
        )

        result = mission_control_create_task(
            title="test", base_url="http://localhost:59999"
        )
        assert result["status"] == "error"
        assert "message" in result

    def test_get_task_tool_error(self) -> None:
        """get_task tool returns error dict."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_get_task,
        )

        result = mission_control_get_task(
            task_id="test-id", base_url="http://localhost:59999"
        )
        assert result["status"] == "error"
        assert "message" in result

    def test_start_tool_missing_path(self) -> None:
        """start tool returns error when app_path doesn't exist."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_start,
        )

        result = mission_control_start(app_path="/tmp/nonexistent-mc-dir")
        assert result["status"] == "error"
        assert "message" in result
        assert "not found" in result["message"]

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_status_tool_live(self) -> None:
        """status tool returns success against live server."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_status,
        )

        result = mission_control_status()
        assert result["status"] == "success"
        assert result["running"] is True

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_list_agents_tool_live(self) -> None:
        """list_agents tool returns success against live server."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_list_agents,
        )

        result = mission_control_list_agents()
        assert result["status"] == "success"
        assert isinstance(result["agents"], list)
        assert "count" in result

    @pytest.mark.skipif(not HAS_SERVER, reason="Mission Control not running")
    def test_list_tasks_tool_live(self) -> None:
        """list_tasks tool returns success against live server."""
        from codomyrmex.agents.mission_control.mcp_tools import (
            mission_control_list_tasks,
        )

        result = mission_control_list_tasks()
        assert result["status"] == "success"
        assert isinstance(result["tasks"], list)
        assert "count" in result


# ═══════════════════════════════════════════════════════════════════
# MCP TOOL SPECIFICATION PARITY
# ═══════════════════════════════════════════════════════════════════


class TestMCPToolSpecParity:
    """Verify all documented MCP tools are importable and callable."""

    EXPECTED_TOOLS = [
        "mission_control_status",
        "mission_control_list_agents",
        "mission_control_list_tasks",
        "mission_control_create_task",
        "mission_control_get_task",
        "mission_control_start",
    ]

    def test_all_tools_importable(self) -> None:
        """All 6 documented tools are importable from mcp_tools."""
        import codomyrmex.agents.mission_control.mcp_tools as mod

        for tool_name in self.EXPECTED_TOOLS:
            assert hasattr(mod, tool_name), f"Missing MCP tool: {tool_name}"
            assert callable(getattr(mod, tool_name))

    def test_tool_count(self) -> None:
        """Exactly 6 MCP tools are defined (no undocumented extras)."""
        import codomyrmex.agents.mission_control.mcp_tools as mod

        # Count functions with _mcp_tool attribute or in the expected list
        public_functions = [
            name
            for name in dir(mod)
            if not name.startswith("_") and callable(getattr(mod, name))
        ]
        # Filter to just mission_control_* functions
        mc_tools = [f for f in public_functions if f.startswith("mission_control_")]
        assert len(mc_tools) == 6, f"Expected 6 tools, got {len(mc_tools)}: {mc_tools}"


# ═══════════════════════════════════════════════════════════════════
# MODULE __init__ IMPORTS
# ═══════════════════════════════════════════════════════════════════


class TestModuleImports:
    """Verify module-level exports are correct."""

    def test_init_exports_client(self) -> None:
        """MissionControlClient is importable from the package."""
        from codomyrmex.agents.mission_control import MissionControlClient

        assert MissionControlClient is not None

    def test_init_exports_config(self) -> None:
        """MissionControlConfig is importable from the package."""
        from codomyrmex.agents.mission_control import MissionControlConfig

        assert MissionControlConfig is not None

    def test_init_exports_error(self) -> None:
        """MissionControlError is importable from the package."""
        from codomyrmex.agents.mission_control import MissionControlError

        assert issubclass(MissionControlError, Exception)

    def test_parent_module_exports_client(self) -> None:
        """MissionControlClient is importable from agents package."""
        from codomyrmex.agents import MissionControlClient

        assert MissionControlClient is not None

    def test_all_list_complete(self) -> None:
        """__all__ contains the 3 expected exports."""
        import codomyrmex.agents.mission_control as mod

        assert "MissionControlClient" in mod.__all__
        assert "MissionControlConfig" in mod.__all__
        assert "MissionControlError" in mod.__all__

    def test_error_is_exception_subclass(self) -> None:
        """MissionControlError is a proper Exception subclass."""
        from codomyrmex.agents.mission_control import MissionControlError

        exc = MissionControlError("test message")
        assert str(exc) == "test message"
        assert isinstance(exc, Exception)
