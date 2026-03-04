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
        """Verify adapter stores agent reference behavior."""
        assert adapter.agent is stub_agent

    def test_adapter_has_logger(self, adapter: ClaudeIntegrationAdapter):
        """Verify adapter has logger behavior."""
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
        """Verify returns string behavior."""
        result = adapter.adapt_for_ai_code_editing(prompt="Create a hello function")
        assert isinstance(result, str)

    def test_passes_prompt_to_agent(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify passes prompt to agent behavior."""
        adapter.adapt_for_ai_code_editing(prompt="Create a fib function", language="python")
        assert stub_agent.last_request is not None
        assert "fib" in stub_agent.last_request.prompt

    def test_context_includes_language(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify context includes language behavior."""
        adapter.adapt_for_ai_code_editing(prompt="test", language="rust")
        ctx = stub_agent.last_request.context
        assert ctx["language"] == "rust"

    def test_context_includes_system_prompt(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify context includes system prompt behavior."""
        adapter.adapt_for_ai_code_editing(prompt="test", language="go")
        ctx = stub_agent.last_request.context
        assert "system" in ctx
        assert "go" in ctx["system"].lower()

    def test_context_code_prepended(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify context code prepended behavior."""
        adapter.adapt_for_ai_code_editing(
            prompt="Add type hints",
            context_code="def add(a, b): return a + b",
        )
        assert "Existing code context" in stub_agent.last_request.prompt

    def test_style_affects_system_prompt(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify style affects system prompt behavior."""
        adapter.adapt_for_ai_code_editing(prompt="test", style="functional")
        assert "functional" in stub_agent.last_request.context["system"].lower()

    def test_error_raises_runtime_error(self):
        """Verify error raises runtime error behavior."""
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
        """Verify yields chunks behavior."""
        chunks = list(adapter.adapt_for_ai_code_editing_stream(prompt="test"))
        assert len(chunks) > 0


# =====================================================================
# adapt_for_llm
# =====================================================================


class TestAdaptForLlm:
    """Tests for the LLM adapter method."""

    def test_returns_dict_with_expected_keys(self, adapter: ClaudeIntegrationAdapter):
        """Verify returns dict with expected keys behavior."""
        messages = [{"role": "user", "content": "Hello"}]
        result = adapter.adapt_for_llm(messages=messages)
        assert "content" in result
        assert "model" in result
        assert "usage" in result
        assert "metadata" in result

    def test_extracts_system_message(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify extracts system message behavior."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
        ]
        adapter.adapt_for_llm(messages=messages)
        ctx = stub_agent.last_request.context
        assert ctx.get("system") == "You are helpful"

    def test_system_prompt_parameter_takes_precedence(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify system prompt parameter takes precedence behavior."""
        messages = [
            {"role": "system", "content": "from message"},
            {"role": "user", "content": "Hi"},
        ]
        adapter.adapt_for_llm(messages=messages, system_prompt="from parameter")
        ctx = stub_agent.last_request.context
        assert ctx.get("system") == "from parameter"

    def test_usage_dict_has_token_counts(self, adapter: ClaudeIntegrationAdapter):
        """Verify usage dict has token counts behavior."""
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
        """Verify returns dict with success behavior."""
        result = adapter.adapt_for_code_execution(code="x = 1")
        assert isinstance(result, dict)
        assert result["success"] is True

    def test_analysis_type_in_context(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify analysis type in context behavior."""
        adapter.adapt_for_code_execution(code="x = 1", analysis_type="security")
        ctx = stub_agent.last_request.context
        assert ctx["analysis_type"] == "security"

    def test_code_included_in_prompt(self, adapter: ClaudeIntegrationAdapter, stub_agent: StubClaudeAgent):
        """Verify code included in prompt behavior."""
        adapter.adapt_for_code_execution(code="import os; os.system('rm -rf /')")
        assert "os.system" in stub_agent.last_request.prompt

    def test_error_response_includes_error_key(self):
        """Verify error response includes error key behavior."""
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
        """Verify returns dict with expected keys behavior."""
        result = adapter.adapt_for_code_refactoring(
            code="def add(a,b): return a+b",
            instruction="Add type hints",
        )
        assert "success" in result
        assert "refactored_code" in result
        assert "original_code" in result
        assert "instruction" in result

    def test_original_code_preserved(self, adapter: ClaudeIntegrationAdapter):
        """Verify original code preserved behavior."""
        original = "def add(a,b): return a+b"
        result = adapter.adapt_for_code_refactoring(code=original, instruction="Rename")
        assert result["original_code"] == original


# =====================================================================
# Private helpers
# =====================================================================


class TestCodeExtraction:
    """Tests for _extract_code_from_response."""

    def test_extracts_from_language_code_block(self, adapter: ClaudeIntegrationAdapter):
        """Verify extracts from language code block behavior."""
        response = "Here is code:\n```python\ndef foo(): pass\n```\nDone."
        result = adapter._extract_code_from_response(response, "python")
        assert result == "def foo(): pass"

    def test_extracts_from_generic_code_block(self, adapter: ClaudeIntegrationAdapter):
        """Verify extracts from generic code block behavior."""
        response = "```\nprint('hi')\n```"
        result = adapter._extract_code_from_response(response, "python")
        assert result == "print('hi')"

    def test_returns_stripped_original_when_no_block(self, adapter: ClaudeIntegrationAdapter):
        """Verify returns stripped original when no block behavior."""
        response = "  just plain text  "
        result = adapter._extract_code_from_response(response, "python")
        assert result == "just plain text"


class TestAnalysisOutputParsing:
    """Tests for _parse_analysis_output."""

    def test_parses_issues(self, adapter: ClaudeIntegrationAdapter):
        """Verify parses issues behavior."""
        output = "Issues found:\n- Missing null check\n- Unused variable"
        result = adapter._parse_analysis_output(output)
        assert len(result["issues"]) == 2

    def test_parses_recommendations(self, adapter: ClaudeIntegrationAdapter):
        """Verify parses recommendations behavior."""
        output = "Recommendations:\n- Use constants\n- Add logging"
        result = adapter._parse_analysis_output(output)
        assert len(result["recommendations"]) == 2

    def test_empty_output_returns_empty_lists(self, adapter: ClaudeIntegrationAdapter):
        """Verify empty output returns empty lists behavior."""
        result = adapter._parse_analysis_output("")
        assert result["issues"] == []
        assert result["recommendations"] == []


class TestSystemPromptBuilding:
    """Tests for _build_code_generation_system_prompt."""

    def test_includes_language(self, adapter: ClaudeIntegrationAdapter):
        """Verify includes language behavior."""
        prompt = adapter._build_code_generation_system_prompt("rust")
        assert "rust" in prompt.lower()

    def test_style_hint_appended(self, adapter: ClaudeIntegrationAdapter):
        """Verify style hint appended behavior."""
        prompt = adapter._build_code_generation_system_prompt("python", style="oop")
        assert "object-oriented" in prompt.lower()

    def test_unknown_style_ignored(self, adapter: ClaudeIntegrationAdapter):
        """Verify unknown style ignored behavior."""
        prompt_no_style = adapter._build_code_generation_system_prompt("python")
        prompt_bad_style = adapter._build_code_generation_system_prompt("python", style="nonexistent")
        assert prompt_no_style == prompt_bad_style
