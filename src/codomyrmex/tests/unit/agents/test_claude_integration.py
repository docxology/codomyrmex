"""Unit tests for the ClaudeIntegrationAdapter.

Tests adapter construction, prompt building, code extraction, and
analysis parsing — all without requiring API keys or network access.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from codomyrmex.agents.claude import ClaudeIntegrationAdapter
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)

# =====================================================================
# Stub agent (no API key required)
# =====================================================================


class StubClaudeAgent(BaseAgent):
    """Minimal agent stub that returns canned responses."""

    def __init__(self, response_content: str = "stub response", error: str | None = None):
        super().__init__(
            name="stub-claude",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
            ],
        )
        self._response_content = response_content
        self._error = error
        self.last_request: AgentRequest | None = None

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        self.last_request = request
        return AgentResponse(
            content=self._response_content,
            error=self._error,
            execution_time=0.01,
            tokens_used=10,
            metadata={"usage": {"input_tokens": 5, "output_tokens": 5}},
        )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        self.last_request = request
        yield self._response_content


# =====================================================================
# Fixtures
# =====================================================================


@pytest.fixture
def stub_agent() -> StubClaudeAgent:
    return StubClaudeAgent(response_content="def hello(): pass")


@pytest.fixture
def adapter(stub_agent: StubClaudeAgent) -> ClaudeIntegrationAdapter:
    return ClaudeIntegrationAdapter(stub_agent)


# =====================================================================
# Construction
# =====================================================================


class TestAdapterConstruction:
    """Verify adapter initialises correctly."""

    def test_adapter_stores_agent_reference(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: adapter stores agent reference."""
        assert adapter.agent is stub_agent

    def test_adapter_has_logger(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: adapter has logger."""
        assert adapter.logger is not None

    def test_adapter_inherits_abstract_interface(self):
        """ClaudeIntegrationAdapter is a concrete AgentIntegrationAdapter."""
        from codomyrmex.agents.core.base import AgentIntegrationAdapter

        assert issubclass(ClaudeIntegrationAdapter, AgentIntegrationAdapter)


# =====================================================================
# adapt_for_ai_code_editing
# =====================================================================


class TestAdaptForAiCodeEditing:
    """Tests for the code-generation adapter method."""

    def test_returns_string(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: returns string."""
        result = adapter.adapt_for_ai_code_editing(prompt="Create a hello function")
        assert isinstance(result, str)

    def test_passes_prompt_to_agent(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: passes prompt to agent."""
        adapter.adapt_for_ai_code_editing(prompt="Create a fib function", language="python")
        assert stub_agent.last_request is not None
        assert "fib" in stub_agent.last_request.prompt

    def test_context_includes_language(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: context includes language."""
        adapter.adapt_for_ai_code_editing(prompt="test", language="rust")
        ctx = stub_agent.last_request.context
        assert ctx["language"] == "rust"

    def test_context_includes_system_prompt(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: context includes system prompt."""
        adapter.adapt_for_ai_code_editing(prompt="test", language="go")
        ctx = stub_agent.last_request.context
        assert "system" in ctx
        assert "go" in ctx["system"].lower()

    def test_context_code_prepended(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: context code prepended."""
        adapter.adapt_for_ai_code_editing(
            prompt="Add type hints",
            context_code="def add(a, b): return a + b",
        )
        assert "Existing code context" in stub_agent.last_request.prompt

    def test_style_affects_system_prompt(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: style affects system prompt."""
        adapter.adapt_for_ai_code_editing(prompt="test", style="functional")
        assert "functional" in stub_agent.last_request.context["system"].lower()

    def test_error_raises_runtime_error(self):
        """Test functionality: error raises runtime error."""
        error_agent = StubClaudeAgent(response_content="", error="API failure")
        error_adapter = ClaudeIntegrationAdapter(error_agent)
        with pytest.raises(RuntimeError, match="Code generation failed"):
            error_adapter.adapt_for_ai_code_editing(prompt="test")


# =====================================================================
# adapt_for_ai_code_editing_stream
# =====================================================================


class TestAdaptForAiCodeEditingStream:
    """Tests for the streaming code-generation adapter method."""

    def test_yields_chunks(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: yields chunks."""
        chunks = list(adapter.adapt_for_ai_code_editing_stream(prompt="test"))
        assert len(chunks) > 0


# =====================================================================
# adapt_for_llm
# =====================================================================


class TestAdaptForLlm:
    """Tests for the LLM adapter method."""

    def test_returns_dict_with_expected_keys(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: returns dict with expected keys."""
        messages = [{"role": "user", "content": "Hello"}]
        result = adapter.adapt_for_llm(messages=messages)
        assert "content" in result
        assert "model" in result
        assert "usage" in result
        assert "metadata" in result

    def test_extracts_system_message(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: extracts system message."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
        ]
        adapter.adapt_for_llm(messages=messages)
        ctx = stub_agent.last_request.context
        assert ctx.get("system") == "You are helpful"

    def test_system_prompt_parameter_takes_precedence(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: system prompt parameter takes precedence."""
        messages = [
            {"role": "system", "content": "from message"},
            {"role": "user", "content": "Hi"},
        ]
        adapter.adapt_for_llm(messages=messages, system_prompt="from parameter")
        ctx = stub_agent.last_request.context
        assert ctx.get("system") == "from parameter"

    def test_usage_dict_has_token_counts(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: usage dict has token counts."""
        result = adapter.adapt_for_llm(messages=[{"role": "user", "content": "Hi"}])
        usage = result["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage


# =====================================================================
# adapt_for_code_execution
# =====================================================================


class TestAdaptForCodeExecution:
    """Tests for the code-execution analysis adapter method."""

    def test_returns_dict_with_success(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: returns dict with success."""
        result = adapter.adapt_for_code_execution(code="x = 1")
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_analysis_type_in_context(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: analysis type in context."""
        adapter.adapt_for_code_execution(code="x = 1", analysis_type="security")
        ctx = stub_agent.last_request.context
        assert ctx["analysis_type"] == "security"

    def test_code_included_in_prompt(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Test functionality: code included in prompt."""
        adapter.adapt_for_code_execution(code="import os; os.system('rm -rf /')")
        assert "os.system" in stub_agent.last_request.prompt

    def test_error_response_includes_error_key(self):
        """Test functionality: error response includes error key."""
        error_agent = StubClaudeAgent(response_content="", error="timeout")
        error_adapter = ClaudeIntegrationAdapter(error_agent)
        result = error_adapter.adapt_for_code_execution(code="x = 1")
        assert "error" in result


# =====================================================================
# adapt_for_code_refactoring
# =====================================================================


class TestAdaptForCodeRefactoring:
    """Tests for the code-refactoring adapter method."""

    def test_returns_dict_with_expected_keys(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: returns dict with expected keys."""
        result = adapter.adapt_for_code_refactoring(
            code="def add(a,b): return a+b",
            instruction="Add type hints",
        )
        assert "success" in result
        assert "refactored_code" in result
        assert "original_code" in result
        assert "instruction" in result

    def test_original_code_preserved(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: original code preserved."""
        original = "def add(a,b): return a+b"
        result = adapter.adapt_for_code_refactoring(code=original, instruction="Rename")
        assert result["original_code"] == original


# =====================================================================
# Private helpers
# =====================================================================


class TestCodeExtraction:
    """Tests for _extract_code_from_response."""

    def test_extracts_from_language_code_block(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: extracts from language code block."""
        response = "Here is code:\n```python\ndef foo(): pass\n```\nDone."
        result = adapter._extract_code_from_response(response, "python")
        assert result == "def foo(): pass"

    def test_extracts_from_generic_code_block(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: extracts from generic code block."""
        response = "```\nprint('hi')\n```"
        result = adapter._extract_code_from_response(response, "python")
        assert result == "print('hi')"

    def test_returns_stripped_original_when_no_block(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: returns stripped original when no block."""
        response = "  just plain text  "
        result = adapter._extract_code_from_response(response, "python")
        assert result == "just plain text"


class TestAnalysisOutputParsing:
    """Tests for _parse_analysis_output."""

    def test_parses_issues(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: parses issues."""
        output = "Issues found:\n- Missing null check\n- Unused variable"
        result = adapter._parse_analysis_output(output)
        assert len(result["issues"]) == 2

    def test_parses_recommendations(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: parses recommendations."""
        output = "Recommendations:\n- Use constants\n- Add logging"
        result = adapter._parse_analysis_output(output)
        assert len(result["recommendations"]) == 2

    def test_empty_output_returns_empty_lists(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: empty output returns empty lists."""
        result = adapter._parse_analysis_output("")
        assert result["issues"] == []
        assert result["recommendations"] == []


class TestSystemPromptBuilding:
    """Tests for _build_code_generation_system_prompt."""

    def test_includes_language(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: includes language."""
        prompt = adapter._build_code_generation_system_prompt("rust")
        assert "rust" in prompt.lower()

    def test_style_hint_appended(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: style hint appended."""
        prompt = adapter._build_code_generation_system_prompt("python", style="oop")
        assert "object-oriented" in prompt.lower()

    def test_unknown_style_ignored(self, adapter: ClaudeIntegrationAdapter):
        """Test functionality: unknown style ignored."""
        prompt_no_style = adapter._build_code_generation_system_prompt("python")
        prompt_bad_style = adapter._build_code_generation_system_prompt("python", style="nonexistent")
        assert prompt_no_style == prompt_bad_style
