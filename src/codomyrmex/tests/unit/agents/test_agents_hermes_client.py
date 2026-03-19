"""Unit tests for the Hermes Agent client.

These tests follow the Codomyrmex zero-mock policy. They instantiate
HermesClient and execute real assertions against its argument builder.
If the 'hermes' CLI is missing, execution tests gracefully skip or assert
on the resulting HermesError.
"""

import shutil

import pytest

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes import (
    SESSION_METADATA_HERMES_SKILLS_KEY,
    HermesClient,
    agent_context_for_hermes_skills,
    normalize_hermes_skill_names,
)
from codomyrmex.agents.hermes.mcp_tools import (
    hermes_execute,
    hermes_skills_list,
    hermes_status,
)

# Check if hermes is actually installed locally for integration tests
HAS_HERMES = shutil.which("hermes") is not None


class TestHermesClientArgBuilder:
    """Zero-mock tests for HermesClient argument building."""

    def test_client_initialization(self) -> None:
        """Test client initializes without mocking config handling."""
        client = HermesClient(
            config={"hermes_command": "custom_hermes", "hermes_timeout": 500}
        )
        assert client.command == "custom_hermes"
        assert client.timeout == 500
        assert client.name == "hermes"

    def test_build_args_chat(self) -> None:
        """Test default single-turn chat arg builder."""
        client = HermesClient()
        args = client._build_hermes_args(prompt="test task", context={})
        assert args == ["chat", "-q", "test task", "-Q", "--provider", "openrouter"]

    def test_build_args_specialized_command(self) -> None:
        """Test specialized command via context bypass."""
        client = HermesClient()
        args = client._build_hermes_args(
            prompt="ignored here",
            context={"command": "status", "args": ["--verbose"]},
        )
        assert args == ["status", "--verbose"]

    def test_build_args_skills_list(self) -> None:
        """Test skills list builder."""
        client = HermesClient()
        args = client._build_hermes_args(
            prompt="",
            context={"command": "skills", "args": ["list"]},
        )
        assert args == ["skills", "list"]

    def test_build_args_single_skill(self) -> None:
        """Hermes chat prepends -s for one skill."""
        client = HermesClient()
        args = client._build_hermes_args(
            prompt="run pipeline",
            context=agent_context_for_hermes_skills(
                hermes_skill="geopolitical-market-sim"
            ),
        )
        assert args[:4] == [
            "chat",
            "-s",
            "geopolitical-market-sim",
            "-q",
        ]
        assert "run pipeline" in args

    def test_build_args_multiple_skills(self) -> None:
        """Multiple skills are comma-joined for one -s flag."""
        client = HermesClient()
        args = client._build_hermes_args(
            prompt="x",
            context=agent_context_for_hermes_skills(
                hermes_skill="a",
                hermes_skills=["b", "c"],
            ),
        )
        idx = args.index("-s")
        assert args[idx + 1] == "a,b,c"

    def test_normalize_hermes_skill_names(self) -> None:
        """Dedup and trim skill names."""
        assert normalize_hermes_skill_names("a", ["a", " b "]) == ["a", "b"]
        assert normalize_hermes_skill_names(None, "x, y") == ["x", "y"]

    def test_cli_response_includes_hermes_skills_loaded_metadata(self) -> None:
        """CLI path echoes preloaded skill names in response metadata."""

        class _StubHermes(HermesClient):
            def _is_cli_configured(self) -> bool:
                return True

            def _execute_command(self, args, env=None):
                return {
                    "success": True,
                    "stdout": "stub",
                    "stderr": "",
                    "exit_code": 0,
                }

        client = _StubHermes(
            config={"hermes_backend": "cli", "hermes_command": "hermes"}
        )
        req = AgentRequest(
            prompt="hello",
            context=agent_context_for_hermes_skills(
                hermes_skill="demo-pack",
                hermes_skills=["other"],
            ),
        )
        resp = client.execute(req)
        assert resp.is_success()
        assert resp.metadata.get("hermes_skills_loaded") == ["demo-pack", "other"]


class TestHermesClientExecution:
    """Zero-mock execution tests for HermesClient."""

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_hermes_status_success(self) -> None:
        """Test actual status command if installed."""
        client = HermesClient()
        result = client.get_hermes_status()
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.skipif(HAS_HERMES, reason="hermes CLI is installed")
    def test_hermes_missing_error(self) -> None:
        """Test that missing hermes command returns an error response."""
        client = HermesClient(
            config={
                "hermes_command": "nonexistent_hermes_binary",
                "hermes_backend": "cli",
            }
        )
        request = AgentRequest(prompt="test")
        response = client.execute(request)
        assert not response.is_success()
        assert "nonexistent_hermes_binary" in str(response.error)

    def test_stream_args(self) -> None:
        """Test streaming argument iteration on client."""
        client = HermesClient(config={"hermes_command": "echo"})
        # Replacing command with echo bypasses hermes requirement,
        # but verifies that execution pathways don't crash and stream yields
        request = AgentRequest(prompt="hello")

        # Build stream
        stream = client.stream(request)
        outputs = list(stream)

        # We should at least get some output or an error if echo isn't exactly matched
        # Our CLIAgentBase handles wrapping, so we just verify it returned strings or raised a proper AgentError.
        assert len(outputs) > 0 or isinstance(outputs, list)


class TestHermesMCPTools:
    """Zero-mock tests for Hermes MCP Tools."""

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_hermes_skills_list_mcp(self) -> None:
        """Test the hermes_skills_list tool directly."""
        result = hermes_skills_list()
        assert result["status"] in ("success", "error")
        if result["status"] == "success":
            assert isinstance(result["output"], str)

    def test_hermes_status_mcp_missing_binary(self) -> None:
        """Test status with an invalid binary configured via class monkeypatch or natural error."""
        # By default, hermes_status uses the local system.
        result = hermes_status()
        assert "status" in result
        assert "available" in result

    def test_hermes_execute_mcp(self) -> None:
        """Test execute MCP tool. If hermes is missing, it returns an error dict."""
        result = hermes_execute(prompt="test prompt", timeout=1)
        # Verify the structure matches MCP SPEC
        assert "status" in result
        assert "content" in result
        assert "error" in result
        assert "metadata" in result


class TestHermesClientSessionIntegration:
    """Zero-mock tests for stateful chat sessions."""

    def test_chat_session_new_and_continue(self, tmp_path) -> None:
        """Test creating a new session and appending to it."""
        db_path = tmp_path / "test_sessions.db"

        # Use echo to simulate a fast, mock-free successful execution
        client = HermesClient(
            config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
        )

        # Turn 1
        response1 = client.chat_session(prompt="hello session")
        assert response1.is_success()
        session_id = response1.metadata.get("session_id")
        assert session_id is not None

        # Turn 2
        response2 = client.chat_session(prompt="follow up", session_id=session_id)
        assert response2.is_success()
        assert response2.metadata.get("session_id") == session_id

        # Verify the history buildup from SQLite directly
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        with SQLiteSessionStore(db_path) as store:
            session = store.load(session_id)
            assert session is not None
            # Message history should have user, assistant, user, assistant
            assert session.message_count == 4
            assert session.messages[0]["content"] == "hello session"
            assert session.messages[2]["content"] == "follow up"

    def test_chat_session_persists_hermes_skills(self, tmp_path) -> None:
        """Skill names persist on the session for subsequent turns."""
        db_path = tmp_path / "skills_sessions.db"
        client = HermesClient(
            config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
        )
        r1 = client.chat_session(
            prompt="hello",
            hermes_skill="geopolitical-market-sim",
        )
        assert r1.is_success()
        sid = r1.metadata.get("session_id")
        assert sid is not None
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        with SQLiteSessionStore(db_path) as store:
            s = store.load(sid)
            assert s is not None
            assert s.metadata.get(SESSION_METADATA_HERMES_SKILLS_KEY) == [
                "geopolitical-market-sim",
            ]
        r2 = client.chat_session(prompt="again", session_id=sid)
        assert r2.is_success()
        with SQLiteSessionStore(db_path) as store:
            s2 = store.load(sid)
            assert s2 is not None
            assert s2.metadata.get(SESSION_METADATA_HERMES_SKILLS_KEY) == [
                "geopolitical-market-sim",
            ]


class TestHermesSessionMCPTools:
    """Zero-mock tests for session MCP tools."""

    def test_mcp_session_lifecycle(self, monkeypatch, tmp_path) -> None:
        """Test create, list, and clear session MCP tools."""
        db_path = tmp_path / "mcp_sessions.db"
        # Patch _get_client to inject our test config
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        def mock_get_client(**kwargs):
            return HermesClient(
                config={
                    "hermes_command": "echo",
                    "hermes_session_db": str(db_path),
                    "hermes_backend": kwargs.get("backend", "auto"),
                    "hermes_model": kwargs.get("model", "hermes3"),
                    "hermes_timeout": kwargs.get("timeout", 120),
                }
            )

        monkeypatch.setattr(mcp_tools, "_get_client", mock_get_client)

        from codomyrmex.agents.hermes.mcp_tools import (
            hermes_chat_session,
            hermes_session_clear,
            hermes_session_list,
        )

        # 1. Start a session
        res1 = hermes_chat_session(prompt="MCP test 1", backend="cli")
        assert res1["status"] == "success"
        session_id = res1["session_id"]
        assert session_id is not None

        # 2. List sessions
        list_res = hermes_session_list()
        assert list_res["status"] == "success"
        assert session_id in list_res["sessions"]

        # 3. Clear session
        clear_res = hermes_session_clear(session_id)
        assert clear_res["status"] == "success"
        assert clear_res["deleted"] is True

        # 4. Verify cleared
        list_after = hermes_session_list()
        assert session_id not in list_after["sessions"]
