"""Tests for agents.core.base — BaseAgent, AgentRequest, AgentResponse.

Covers:
- AgentRequest/AgentResponse dataclass initialization and defaults
- AgentCapabilities enum values
- BaseAgent.execute() delegates to _execute_impl()
- BaseAgent.execute() routes exceptions to AgentResponse.error
- BaseAgent.plan() / act() / observe() default implementations
- BaseAgent.get_capabilities() and supports_capability()
- AgentResponse.is_success() reflects error presence
"""

import pytest

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)

# ---------------------------------------------------------------------------
# Concrete BaseAgent subclass for testing
# ---------------------------------------------------------------------------

class _EchoAgent(BaseAgent):
    """Minimal concrete agent that echoes the prompt back."""

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            content=f"echo: {request.prompt}",
            request_id=request.id,
        )

    def _stream_impl(self, request: AgentRequest):
        yield f"stream: {request.prompt}"


class _RaisingAgent(BaseAgent):
    """Concrete agent that always raises an exception."""

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        raise RuntimeError("intentional test failure")

    def _stream_impl(self, request: AgentRequest):
        raise RuntimeError("intentional stream failure")
        yield  # pragma: no cover


# ---------------------------------------------------------------------------
# AgentCapabilities enum
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAgentCapabilities:
    """Tests for AgentCapabilities enum."""

    def test_enum_members_exist(self):
        """Key capability values are present in the enum."""
        assert AgentCapabilities.CODE_GENERATION.value == "code_generation"
        assert AgentCapabilities.STREAMING.value == "streaming"
        assert AgentCapabilities.TOOL_USE.value == "tool_use"

    def test_enum_is_iterable(self):
        """AgentCapabilities can be iterated."""
        caps = list(AgentCapabilities)
        assert len(caps) > 5


# ---------------------------------------------------------------------------
# AgentRequest
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAgentRequest:
    """Tests for AgentRequest dataclass."""

    def test_minimal_construction(self):
        """AgentRequest requires only prompt; defaults are populated."""
        req = AgentRequest(prompt="hello")
        assert req.prompt == "hello"
        assert req.context == {}
        assert req.capabilities == []
        assert req.metadata == {}
        assert req.timeout is None
        assert req.id is None

    def test_explicit_fields(self):
        """AgentRequest accepts all optional fields."""
        req = AgentRequest(
            prompt="analyze",
            context={"lang": "python"},
            capabilities=[AgentCapabilities.CODE_ANALYSIS],
            timeout=30,
            metadata={"version": "1"},
            id="req-001",
        )
        assert req.context == {"lang": "python"}
        assert AgentCapabilities.CODE_ANALYSIS in req.capabilities
        assert req.timeout == 30
        assert req.id == "req-001"

    def test_context_is_isolated(self):
        """Two AgentRequests with default context do not share the same dict."""
        r1 = AgentRequest(prompt="a")
        r2 = AgentRequest(prompt="b")
        r1.context["key"] = "val"
        assert "key" not in r2.context


# ---------------------------------------------------------------------------
# AgentResponse
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAgentResponse:
    """Tests for AgentResponse dataclass."""

    def test_success_response(self):
        """Response without error is_success() returns True."""
        resp = AgentResponse(content="ok")
        assert resp.is_success() is True
        assert resp.error is None

    def test_error_response(self):
        """Response with error is_success() returns False."""
        resp = AgentResponse(content="", error="something went wrong")
        assert resp.is_success() is False
        assert resp.error == "something went wrong"

    def test_metadata_defaults_to_empty_dict(self):
        """Metadata defaults to empty dict, not None."""
        resp = AgentResponse(content="x")
        assert resp.metadata == {}


# ---------------------------------------------------------------------------
# BaseAgent — execute() delegation and error routing
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBaseAgentExecute:
    """Tests for BaseAgent.execute() method."""

    def setup_method(self):
        self.echo = _EchoAgent(
            name="echo",
            capabilities=[AgentCapabilities.TEXT_COMPLETION],
        )
        self.raiser = _RaisingAgent(
            name="raiser",
            capabilities=[AgentCapabilities.TEXT_COMPLETION],
        )

    def test_execute_delegates_to_impl(self):
        """execute() calls _execute_impl and returns its result."""
        resp = self.echo.execute(AgentRequest(prompt="test"))
        assert resp.content == "echo: test"
        assert resp.is_success() is True

    def test_execute_routes_exception_to_error(self):
        """execute() catches exceptions from _execute_impl and returns AgentResponse with error."""
        resp = self.raiser.execute(AgentRequest(prompt="crash"))
        assert resp.is_success() is False
        assert "intentional test failure" in resp.error
        assert resp.content == ""

    def test_execute_error_metadata_has_error_type(self):
        """execute() error response metadata contains error_type key."""
        resp = self.raiser.execute(AgentRequest(prompt="crash"))
        assert resp.metadata.get("error_type") == "RuntimeError"

    def test_execute_empty_prompt_raises_value_error(self):
        """execute() raises ValueError for empty prompt, which is caught and returned as error."""
        resp = self.echo.execute(AgentRequest(prompt=""))
        assert resp.is_success() is False
        assert "Prompt" in resp.error or "prompt" in resp.error.lower()

    def test_execute_preserves_request_id(self):
        """execute() passes request.id through to the response."""
        resp = self.echo.execute(AgentRequest(prompt="hello", id="req-xyz"))
        assert resp.request_id == "req-xyz"


# ---------------------------------------------------------------------------
# BaseAgent — stream() error routing
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBaseAgentStream:
    """Tests for BaseAgent.stream() method."""

    def setup_method(self):
        self.echo = _EchoAgent(
            name="echo",
            capabilities=[AgentCapabilities.STREAMING],
        )
        self.raiser = _RaisingAgent(
            name="raiser",
            capabilities=[AgentCapabilities.STREAMING],
        )

    def test_stream_yields_chunks(self):
        """stream() yields string chunks from _stream_impl."""
        chunks = list(self.echo.stream(AgentRequest(prompt="hi")))
        assert len(chunks) == 1
        assert "stream: hi" in chunks[0]

    def test_stream_routes_exception_to_error_chunk(self):
        """stream() yields an error string when _stream_impl raises."""
        chunks = list(self.raiser.stream(AgentRequest(prompt="crash")))
        assert len(chunks) >= 1
        assert "Error:" in chunks[0] or "error" in chunks[0].lower()


# ---------------------------------------------------------------------------
# BaseAgent — plan / act / observe default implementations
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBaseAgentPlanActObserve:
    """Tests for BaseAgent.plan(), act(), and observe() defaults."""

    def setup_method(self):
        self.agent = _EchoAgent(
            name="echo",
            capabilities=[AgentCapabilities.TEXT_COMPLETION],
        )

    def test_plan_returns_single_step_list(self):
        """plan() default returns a one-item list with the prompt."""
        req = AgentRequest(prompt="do something")
        steps = self.agent.plan(req)
        assert steps == ["do something"]

    def test_act_executes_action_string(self):
        """act() wraps the action in an AgentRequest and calls execute()."""
        resp = self.agent.act("test action")
        assert resp.content == "echo: test action"

    def test_observe_extracts_success(self):
        """observe() returns dict with content, success, and error keys."""
        resp = AgentResponse(content="done", error=None)
        obs = self.agent.observe(resp)
        assert obs["content"] == "done"
        assert obs["success"] is True
        assert obs["error"] is None

    def test_observe_extracts_error(self):
        """observe() success is False when response has error."""
        resp = AgentResponse(content="", error="failed")
        obs = self.agent.observe(resp)
        assert obs["success"] is False
        assert obs["error"] == "failed"


# ---------------------------------------------------------------------------
# BaseAgent — capabilities
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBaseAgentCapabilities:
    """Tests for BaseAgent capability methods."""

    def test_get_capabilities_returns_list(self):
        """get_capabilities() returns the capabilities provided at construction."""
        agent = _EchoAgent(
            name="test",
            capabilities=[AgentCapabilities.CODE_GENERATION, AgentCapabilities.STREAMING],
        )
        caps = agent.get_capabilities()
        assert AgentCapabilities.CODE_GENERATION in caps
        assert AgentCapabilities.STREAMING in caps

    def test_supports_capability_true(self):
        """supports_capability() returns True for a supported capability."""
        agent = _EchoAgent(
            name="test",
            capabilities=[AgentCapabilities.TOOL_USE],
        )
        assert agent.supports_capability(AgentCapabilities.TOOL_USE) is True

    def test_supports_capability_false(self):
        """supports_capability() returns False for an unsupported capability."""
        agent = _EchoAgent(
            name="test",
            capabilities=[AgentCapabilities.TOOL_USE],
        )
        assert agent.supports_capability(AgentCapabilities.VISION) is False

    def test_test_connection_default_returns_true(self):
        """test_connection() default implementation returns True."""
        agent = _EchoAgent(name="test", capabilities=[])
        assert agent.test_connection() is True
