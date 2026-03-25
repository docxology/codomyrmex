"""Unit tests for ClaudeTaskExecutionMixin helpers (no API calls)."""

import pytest

from codomyrmex.agents.ai_code_editing._execution import ClaudeTaskExecutionMixin


@pytest.mark.unit
class TestClaudeTaskExecutionMixinHelpers:
    """Exercise mixin methods that do not require a configured Anthropic client."""

    def test_build_task_message_plain(self) -> None:
        m = ClaudeTaskExecutionMixin()
        assert m._build_task_message("do the thing", None) == "Task: do the thing"

    def test_build_task_message_with_context(self) -> None:
        m = ClaudeTaskExecutionMixin()
        out = m._build_task_message("do the thing", "ctx here")
        assert "Context: ctx here" in out
        assert "Task: do the thing" in out

    def test_build_task_system_prompt_nonempty(self) -> None:
        m = ClaudeTaskExecutionMixin()
        prompt = m._build_task_system_prompt()
        assert "Claude Task Master" in prompt
        assert len(prompt) > 40

    def test_extract_code_language_fence(self) -> None:
        m = ClaudeTaskExecutionMixin()
        raw = "```python\nx = 1\n```"
        assert m._extract_code(raw, "python") == "x = 1"

    def test_extract_code_generic_fence(self) -> None:
        m = ClaudeTaskExecutionMixin()
        raw = "```\nplain\n```"
        assert m._extract_code(raw, "python") == "plain"

    def test_extract_code_plain_fallback(self) -> None:
        m = ClaudeTaskExecutionMixin()
        raw = "no fences"
        assert m._extract_code(raw, "rust") == "no fences"
