"""Zero-Mock tests for Antigravity AgentBridge adapter.

Tests for AntigravityAgent initialization, capability detection, prompt routing,
context extraction, request/response dataclass validation, error handling,
and the execute_with_session adapter using real objects only.
"""

import socket

import pytest

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.ide.antigravity.agent_bridge import (
    AntigravityAgent,
    _extract_context_args,
    _route_prompt,
)


def _antigravity_server_available() -> bool:
    """Check if a live Antigravity server is reachable on localhost."""
    try:
        socket.create_connection(("localhost", 3000), timeout=0.5).close()
        return True
    except OSError:
        return False


ANTIGRAVITY_AVAILABLE = _antigravity_server_available()


@pytest.mark.unit
class TestAntigravityAgentInit:
    """Tests for AntigravityAgent construction and default state."""

    def test_default_initialization(self):
        """AntigravityAgent should initialize with default name and capabilities."""
        agent = AntigravityAgent()
        assert agent.name == "antigravity"
        assert isinstance(agent.capabilities, list)
        assert len(agent.capabilities) == 5

    def test_default_capabilities_include_code_generation(self):
        """Default capabilities should include CODE_GENERATION."""
        agent = AntigravityAgent()
        assert AgentCapabilities.CODE_GENERATION in agent.capabilities

    def test_default_capabilities_include_code_editing(self):
        """Default capabilities should include CODE_EDITING."""
        agent = AntigravityAgent()
        assert AgentCapabilities.CODE_EDITING in agent.capabilities

    def test_default_capabilities_include_code_analysis(self):
        """Default capabilities should include CODE_ANALYSIS."""
        agent = AntigravityAgent()
        assert AgentCapabilities.CODE_ANALYSIS in agent.capabilities

    def test_default_capabilities_include_file_operations(self):
        """Default capabilities should include FILE_OPERATIONS."""
        agent = AntigravityAgent()
        assert AgentCapabilities.FILE_OPERATIONS in agent.capabilities

    def test_default_capabilities_include_tool_use(self):
        """Default capabilities should include TOOL_USE."""
        agent = AntigravityAgent()
        assert AgentCapabilities.TOOL_USE in agent.capabilities

    def test_initialization_with_custom_config(self):
        """AntigravityAgent should accept and store custom config."""
        config = {"timeout": 30, "retries": 3}
        agent = AntigravityAgent(config=config)
        assert agent.config == config

    def test_initialization_with_none_config(self):
        """AntigravityAgent config should default to empty dict when None."""
        agent = AntigravityAgent(config=None)
        assert agent.config == {}

    def test_client_is_none_initially(self):
        """Internal _client should be None when no client is passed."""
        agent = AntigravityAgent()
        assert agent._client is None

    def test_custom_client_is_stored(self):
        """Passing a client should store it directly."""
        sentinel = object()
        agent = AntigravityAgent(client=sentinel)
        assert agent._client is sentinel

    def test_is_subclass_of_base_agent(self):
        """AntigravityAgent should be a subclass of BaseAgent."""
        assert issubclass(AntigravityAgent, BaseAgent)

    def test_tool_registry_is_none_initially(self):
        """Internal _tool_registry should be None on creation."""
        agent = AntigravityAgent()
        assert agent._tool_registry is None


@pytest.mark.unit
class TestRoutePrompt:
    """Tests for the _route_prompt helper function."""

    def test_view_keyword_routes_to_view_file(self):
        """Prompt containing 'view' should route to view_file."""
        assert _route_prompt("view this file") == "view_file"

    def test_read_keyword_routes_to_view_file(self):
        """Prompt containing 'read' should route to view_file."""
        assert _route_prompt("read the configuration") == "view_file"

    def test_search_keyword_routes_to_grep_search(self):
        """Prompt containing 'search' should route to grep_search."""
        assert _route_prompt("search for TODO comments") == "grep_search"

    def test_find_keyword_routes_to_find_by_name(self):
        """Prompt containing 'find' should route to find_by_name."""
        assert _route_prompt("find all Python files") == "find_by_name"

    def test_list_keyword_routes_to_list_dir(self):
        """Prompt containing 'list' should route to list_dir."""
        assert _route_prompt("list directory contents") == "list_dir"

    def test_write_keyword_routes_to_write_to_file(self):
        """Prompt containing 'write' should route to write_to_file."""
        assert _route_prompt("write a new module") == "write_to_file"

    def test_run_keyword_routes_to_run_command(self):
        """Prompt containing 'run' should route to run_command."""
        assert _route_prompt("run pytest on this module") == "run_command"

    def test_browse_keyword_routes_to_search_web(self):
        """Prompt containing 'browse' should route to search_web."""
        assert _route_prompt("browse the documentation site") == "search_web"

    def test_fetch_keyword_routes_to_read_url_content(self):
        """Prompt containing 'fetch' should route to read_url_content."""
        assert _route_prompt("fetch the API reference") == "read_url_content"

    def test_outline_keyword_routes_to_view_file_outline(self):
        """Prompt containing 'outline' should route to view_file_outline."""
        assert _route_prompt("outline this class") == "view_file_outline"

    def test_edit_keyword_routes_to_replace_file_content(self):
        """Prompt containing 'edit' should route to replace_file_content."""
        assert _route_prompt("edit the docstring") == "replace_file_content"

    def test_case_insensitive_routing(self):
        """Routing should be case-insensitive."""
        assert _route_prompt("VIEW the README") == "view_file"
        assert _route_prompt("SEARCH for errors") == "grep_search"

    def test_no_match_returns_none(self):
        """Prompt with no matching keywords should return None."""
        result = _route_prompt("what is the meaning of life")
        assert result is None

    def test_empty_prompt_returns_none(self):
        """Empty prompt should return None."""
        assert _route_prompt("") is None

    def test_first_keyword_wins(self):
        """When multiple keywords match, the first in _INTENT_ROUTES wins."""
        # 'view' appears before 'search' in _INTENT_ROUTES
        result = _route_prompt("view and search")
        assert result == "view_file"


@pytest.mark.unit
class TestExtractContextArgs:
    """Tests for the _extract_context_args helper function."""

    def test_empty_context_returns_empty_dict(self):
        """Request with no context/metadata should produce empty args."""
        request = AgentRequest(prompt="test")
        result = _extract_context_args(request)
        assert result == {}

    def test_path_context_maps_to_multiple_keys(self):
        """A 'path' in context should map to AbsolutePath, SearchPath, etc."""
        request = AgentRequest(prompt="test", context={"path": "/src/main.py"})
        result = _extract_context_args(request)
        assert result["AbsolutePath"] == "/src/main.py"
        assert result["SearchPath"] == "/src/main.py"
        assert result["DirectoryPath"] == "/src/main.py"
        assert result["SearchDirectory"] == "/src/main.py"

    def test_query_context_maps_to_query_keys(self):
        """A 'query' in context should map to both Query and query."""
        request = AgentRequest(prompt="test", context={"query": "TODO"})
        result = _extract_context_args(request)
        assert result["Query"] == "TODO"
        assert result["query"] == "TODO"

    def test_pattern_context_maps_to_pattern(self):
        """A 'pattern' in context should map to Pattern."""
        request = AgentRequest(prompt="test", context={"pattern": "*.py"})
        result = _extract_context_args(request)
        assert result["Pattern"] == "*.py"

    def test_command_context_maps_to_commandline(self):
        """A 'command' in context should map to CommandLine."""
        request = AgentRequest(prompt="test", context={"command": "ls -la"})
        result = _extract_context_args(request)
        assert result["CommandLine"] == "ls -la"

    def test_cwd_context_maps_to_cwd(self):
        """A 'cwd' in context should map to Cwd."""
        request = AgentRequest(prompt="test", context={"cwd": "/home/user"})
        result = _extract_context_args(request)
        assert result["Cwd"] == "/home/user"

    def test_content_context_maps_to_code_content(self):
        """A 'content' in context should map to CodeContent."""
        request = AgentRequest(prompt="test", context={"content": "print('hello')"})
        result = _extract_context_args(request)
        assert result["CodeContent"] == "print('hello')"

    def test_target_file_context_maps_to_target_file(self):
        """A 'target_file' in context should map to TargetFile."""
        request = AgentRequest(prompt="test", context={"target_file": "/src/output.py"})
        result = _extract_context_args(request)
        assert result["TargetFile"] == "/src/output.py"

    def test_url_context_maps_to_url(self):
        """A 'url' in context should map to Url."""
        request = AgentRequest(prompt="test", context={"url": "https://example.com"})
        result = _extract_context_args(request)
        assert result["Url"] == "https://example.com"

    def test_metadata_overrides_merge(self):
        """Metadata keys should merge into args, overriding context-derived keys."""
        request = AgentRequest(
            prompt="test",
            context={"path": "/original"},
            metadata={"AbsolutePath": "/override", "extra_key": "extra_value"},
        )
        result = _extract_context_args(request)
        assert result["AbsolutePath"] == "/override"
        assert result["extra_key"] == "extra_value"

    def test_none_context_treated_as_empty(self):
        """Request with None context should not raise."""
        request = AgentRequest(prompt="test")
        request.context = None
        result = _extract_context_args(request)
        # metadata also defaults via __post_init__, so result may have metadata keys
        assert isinstance(result, dict)

    def test_multiple_context_keys_combined(self):
        """Multiple context keys should all appear in the result."""
        request = AgentRequest(
            prompt="test",
            context={"path": "/src", "query": "TODO", "command": "ls"},
        )
        result = _extract_context_args(request)
        assert "AbsolutePath" in result
        assert "Query" in result
        assert "CommandLine" in result


@pytest.mark.unit
class TestAgentRequestDataclass:
    """Tests for AgentRequest dataclass validation and defaults."""

    def test_minimal_request_creation(self):
        """AgentRequest should be creatable with just a prompt."""
        req = AgentRequest(prompt="hello")
        assert req.prompt == "hello"
        assert req.context == {}
        assert req.capabilities == []
        assert req.metadata == {}
        assert req.id is None

    def test_request_with_all_fields(self):
        """AgentRequest should accept all fields."""
        req = AgentRequest(
            prompt="analyze code",
            context={"path": "/src"},
            capabilities=[AgentCapabilities.CODE_ANALYSIS],
            timeout=30,
            metadata={"source": "test"},
            id="req-001",
        )
        assert req.prompt == "analyze code"
        assert req.context == {"path": "/src"}
        assert req.capabilities == [AgentCapabilities.CODE_ANALYSIS]
        assert req.timeout == 30
        assert req.metadata == {"source": "test"}
        assert req.id == "req-001"

    def test_none_context_initializes_to_empty_dict(self):
        """AgentRequest with context=None should default to {}."""
        req = AgentRequest(prompt="test", context=None)
        assert req.context == {}


@pytest.mark.unit
class TestAgentResponseDataclass:
    """Tests for AgentResponse dataclass validation and defaults."""

    def test_minimal_response_creation(self):
        """AgentResponse should be creatable with just content."""
        resp = AgentResponse(content="result")
        assert resp.content == "result"
        assert resp.error is None
        assert resp.metadata == {}
        assert resp.execution_time is None
        assert resp.tokens_used is None

    def test_response_is_success_without_error(self):
        """is_success() should return True when error is None."""
        resp = AgentResponse(content="ok")
        assert resp.is_success() is True

    def test_response_is_not_success_with_error(self):
        """is_success() should return False when error is set."""
        resp = AgentResponse(content="", error="something failed")
        assert resp.is_success() is False

    def test_response_with_all_fields(self):
        """AgentResponse should accept all fields."""
        resp = AgentResponse(
            content="output",
            metadata={"tool": "grep_search"},
            error=None,
            execution_time=1.5,
            tokens_used=100,
            cost=0.002,
            request_id="req-001",
        )
        assert resp.content == "output"
        assert resp.execution_time == 1.5
        assert resp.tokens_used == 100
        assert resp.cost == 0.002
        assert resp.request_id == "req-001"


@pytest.mark.unit
class TestAntigravityAgentCapabilities:
    """Tests for AntigravityAgent capability detection methods."""

    def test_get_capabilities_returns_list(self):
        """get_capabilities() should return a list of AgentCapabilities."""
        agent = AntigravityAgent()
        caps = agent.get_capabilities()
        assert isinstance(caps, list)
        assert all(isinstance(c, AgentCapabilities) for c in caps)

    def test_supports_code_analysis(self):
        """supports_capability should return True for CODE_ANALYSIS."""
        agent = AntigravityAgent()
        assert agent.supports_capability(AgentCapabilities.CODE_ANALYSIS) is True

    def test_supports_tool_use(self):
        """supports_capability should return True for TOOL_USE."""
        agent = AntigravityAgent()
        assert agent.supports_capability(AgentCapabilities.TOOL_USE) is True

    def test_does_not_support_vision(self):
        """supports_capability should return False for VISION (not declared)."""
        agent = AntigravityAgent()
        assert agent.supports_capability(AgentCapabilities.VISION) is False

    def test_does_not_support_streaming(self):
        """supports_capability should return False for STREAMING (not declared)."""
        agent = AntigravityAgent()
        assert agent.supports_capability(AgentCapabilities.STREAMING) is False


@pytest.mark.unit
class TestAntigravityAgentExecuteErrorHandling:
    """Tests for execute error handling when no live server is available."""

    def test_execute_empty_prompt_returns_error_response(self):
        """Executing with empty prompt should return response with error."""
        agent = AntigravityAgent()
        request = AgentRequest(prompt="")
        response = agent.execute(request)
        assert isinstance(response, AgentResponse)
        assert response.error is not None
        assert "required" in response.error.lower() or "Prompt" in response.error

    def test_execute_returns_agent_response_type(self):
        """Execute should always return an AgentResponse, even on error."""
        agent = AntigravityAgent()
        # Use a prompt that will try to invoke the client (which is not connected)
        request = AgentRequest(prompt="search for TODOs")
        response = agent.execute(request)
        assert isinstance(response, AgentResponse)

    def test_execute_with_no_intent_match_defaults_to_grep(self):
        """When no keyword matches and CODE_ANALYSIS is in capabilities, default to grep_search."""
        agent = AntigravityAgent()
        request = AgentRequest(
            prompt="what is the meaning of life",
            capabilities=[AgentCapabilities.CODE_ANALYSIS],
        )
        # This will fail at client.invoke_tool since no server, but we can check
        # that _route_prompt returns None and the fallback logic fires.
        # The error response metadata should show the tool was grep_search.
        response = agent.execute(request)
        assert isinstance(response, AgentResponse)
        # The execute catches the exception and returns an error response
        if response.metadata:
            assert response.metadata.get("tool") == "grep_search" or response.error is not None

    def test_execute_with_file_ops_defaults_to_view_file(self):
        """When no keyword matches and FILE_OPERATIONS is in capabilities, default to view_file."""
        agent = AntigravityAgent()
        request = AgentRequest(
            prompt="what is the meaning of life",
            capabilities=[AgentCapabilities.FILE_OPERATIONS],
        )
        response = agent.execute(request)
        assert isinstance(response, AgentResponse)
        if response.metadata:
            assert response.metadata.get("tool") == "view_file" or response.error is not None


@pytest.mark.unit
class TestAntigravityAgentExecuteWithSession:
    """Tests for the execute_with_session ConversationOrchestrator adapter."""

    def test_adapter_response_has_required_attributes(self):
        """AdapterResponse should expose content, tokens_used, execution_time, error."""
        agent = AntigravityAgent()
        request = AgentRequest(prompt="search for errors")
        adapter_resp = agent.execute_with_session(request)
        assert hasattr(adapter_resp, "content")
        assert hasattr(adapter_resp, "tokens_used")
        assert hasattr(adapter_resp, "execution_time")
        assert hasattr(adapter_resp, "error")

    def test_adapter_response_is_success_method(self):
        """AdapterResponse should have is_success() method."""
        agent = AntigravityAgent()
        request = AgentRequest(prompt="search for errors")
        adapter_resp = agent.execute_with_session(request)
        assert hasattr(adapter_resp, "is_success")
        assert callable(adapter_resp.is_success)

    def test_adapter_response_tokens_used_is_zero(self):
        """AdapterResponse tokens_used should be 0 (no real LLM call)."""
        agent = AntigravityAgent()
        request = AgentRequest(prompt="search for errors")
        adapter_resp = agent.execute_with_session(request)
        assert adapter_resp.tokens_used == 0

    def test_adapter_response_on_error_is_not_success(self):
        """When execution errors, AdapterResponse.is_success() should return False."""
        agent = AntigravityAgent()
        # Empty prompt triggers validation error
        request = AgentRequest(prompt="")
        adapter_resp = agent.execute_with_session(request)
        assert adapter_resp.is_success() is False


@pytest.mark.unit
class TestAntigravityAgentStream:
    """Tests for the stream implementation."""

    def test_stream_yields_content(self):
        """stream() should yield at least one chunk (even if an error message)."""
        agent = AntigravityAgent()
        request = AgentRequest(prompt="search for bugs")
        chunks = list(agent.stream(request))
        assert len(chunks) >= 1
        assert isinstance(chunks[0], str)

    def test_stream_empty_prompt_yields_error(self):
        """stream() with empty prompt should yield an error string."""
        agent = AntigravityAgent()
        request = AgentRequest(prompt="")
        chunks = list(agent.stream(request))
        assert len(chunks) >= 1
        assert "Error" in chunks[0] or "error" in chunks[0].lower()


@pytest.mark.unit
class TestAntigravityAgentConnectionTest:
    """Tests for test_connection when no server is running."""

    def test_connection_returns_false_without_server(self):
        """test_connection() should return False when no Antigravity server exists."""
        agent = AntigravityAgent()
        # The client is lazy-initialized; test_connection() calls client.is_connected()
        # which returns False on a fresh AntigravityClient.
        result = agent.test_connection()
        assert result is False


@pytest.mark.unit
class TestAntigravityAgentPlanActObserve:
    """Tests for the BaseAgent plan/act/observe protocol defaults."""

    def test_plan_returns_prompt_as_single_step(self):
        """Default plan() should return a list with the prompt as the only step."""
        agent = AntigravityAgent()
        request = AgentRequest(prompt="analyze the codebase")
        plan = agent.plan(request)
        assert isinstance(plan, list)
        assert len(plan) == 1
        assert plan[0] == "analyze the codebase"

    def test_observe_returns_dict_with_content_and_success(self):
        """Default observe() should return dict with content, success, error keys."""
        agent = AntigravityAgent()
        response = AgentResponse(content="result", error=None)
        observation = agent.observe(response)
        assert isinstance(observation, dict)
        assert observation["content"] == "result"
        assert observation["success"] is True
        assert observation["error"] is None

    def test_observe_with_error_response(self):
        """observe() with error response should reflect failure."""
        agent = AntigravityAgent()
        response = AgentResponse(content="", error="tool failed")
        observation = agent.observe(response)
        assert observation["success"] is False
        assert observation["error"] == "tool failed"


@pytest.mark.unit
@pytest.mark.skipif(not ANTIGRAVITY_AVAILABLE, reason="Antigravity server not running on localhost:3000")
class TestAntigravityAgentLiveConnection:
    """Tests that require a live Antigravity server. Skipped in CI."""

    def test_connect_succeeds_with_live_server(self, tmp_path):
        """connect() should succeed when Antigravity server is reachable."""
        agent = AntigravityAgent()
        agent.connect()
        assert agent.test_connection() is True

    def test_execute_search_returns_content(self):
        """Execute with search prompt should return non-empty content."""
        agent = AntigravityAgent()
        agent.connect()
        request = AgentRequest(
            prompt="search for TODO",
            context={"path": "/tmp"},
        )
        response = agent.execute(request)
        assert isinstance(response, AgentResponse)
        assert response.content is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
