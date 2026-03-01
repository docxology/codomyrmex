"""Unit tests for agents.llm_client module.

Tests AgentRequest dataclass, _OllamaResponse dataclass, and OllamaClient
construction. Network-dependent tests (actual Ollama calls) are skipped
when no Ollama server is reachable.
"""
import pytest

try:
    from codomyrmex.agents.llm_client import AgentRequest, _OllamaResponse, OllamaClient
    LLM_CLIENT_AVAILABLE = True
except ImportError:
    LLM_CLIENT_AVAILABLE = False

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# AgentRequest
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="agents.llm_client not importable")
class TestAgentRequest:
    """Tests for the AgentRequest dataclass."""

    def test_basic_construction(self):
        req = AgentRequest(prompt="hello")
        assert req.prompt == "hello"
        assert req.metadata is None

    def test_prompt_required(self):
        with pytest.raises(TypeError):
            AgentRequest()  # prompt is required (no default)

    def test_with_metadata(self):
        meta = {"source": "cli", "version": 1}
        req = AgentRequest(prompt="test", metadata=meta)
        assert req.metadata == meta
        assert req.metadata["source"] == "cli"

    def test_metadata_defaults_to_none(self):
        req = AgentRequest(prompt="x")
        assert req.metadata is None

    def test_prompt_empty_string_is_valid(self):
        req = AgentRequest(prompt="")
        assert req.prompt == ""

    def test_prompt_multiline(self):
        multi = "line1\nline2\nline3"
        req = AgentRequest(prompt=multi)
        assert "\n" in req.prompt
        assert req.prompt.count("\n") == 2


# ---------------------------------------------------------------------------
# _OllamaResponse
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="agents.llm_client not importable")
class TestOllamaResponse:
    """Tests for the _OllamaResponse dataclass."""

    def test_default_construction(self):
        resp = _OllamaResponse()
        assert resp.content == ""
        assert resp.tokens_used == 0
        assert resp.execution_time == 0.0

    def test_is_success_returns_true(self):
        resp = _OllamaResponse(content="ok", tokens_used=5, execution_time=0.1)
        assert resp.is_success() is True

    def test_is_success_with_empty_content(self):
        resp = _OllamaResponse()
        assert resp.is_success() is False  # empty content is not a success

    def test_with_content(self):
        resp = _OllamaResponse(content="hello world")
        assert resp.content == "hello world"

    def test_custom_tokens_and_time(self):
        resp = _OllamaResponse(content="x", tokens_used=42, execution_time=1.5)
        assert resp.tokens_used == 42
        assert resp.execution_time == 1.5

    def test_execution_time_zero_by_default(self):
        resp = _OllamaResponse(content="y")
        assert resp.execution_time == 0.0


# ---------------------------------------------------------------------------
# OllamaClient construction (no network required)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="agents.llm_client not importable")
class TestOllamaClientConstruction:
    """Tests for OllamaClient __init__ without requiring a running server."""

    def test_default_model_and_url(self):
        client = OllamaClient()
        assert client.model == "llama3"
        assert "localhost" in client.base_url or "127.0.0.1" in client.base_url

    def test_custom_model(self):
        client = OllamaClient(model="codellama:7b")
        assert client.model == "codellama:7b"

    def test_custom_base_url(self):
        client = OllamaClient(base_url="http://gpu-box:11434")
        assert client.base_url == "http://gpu-box:11434"

    def test_session_manager_initially_none(self):
        client = OllamaClient()
        assert client.session_manager is None

    def test_create_session(self):
        client = OllamaClient()
        client.create_session("sess-1")
        assert client.session_manager is not None
        assert "sess-1" in client.session_manager

    def test_close_session(self):
        client = OllamaClient()
        client.create_session("sess-2")
        client.close_session("sess-2")
        assert "sess-2" not in client.session_manager

    def test_close_nonexistent_session_is_noop(self):
        client = OllamaClient()
        client.close_session("no-such-session")  # should not raise
