"""Tests for codomyrmex.agents.agentic_seek.agent_router.

Zero-mock tests covering keyword classification, complexity
estimation, heuristic fallbacks, and edge cases.
"""

import pytest

from codomyrmex.agents.agentic_seek.agent_router import (
    AgenticSeekRouter,
    _score,
)
from codomyrmex.agents.agentic_seek.agent_types import AgenticSeekAgentType


@pytest.fixture
def router() -> AgenticSeekRouter:
    return AgenticSeekRouter()


# ===================================================================
# classify_query – keyword matching
# ===================================================================

class TestClassifyQueryKeywords:
    """Verify keyword-based classification for each agent type."""

    def test_coder_python_script(self, router):
        result = router.classify_query("Write a Python script to sort a list")
        assert result is AgenticSeekAgentType.CODER

    def test_coder_debug(self, router):
        result = router.classify_query("Debug this code that crashes on line 10")
        assert result is AgenticSeekAgentType.CODER

    def test_browser_search(self, router):
        result = router.classify_query("Search the web for AI news articles")
        assert result is AgenticSeekAgentType.BROWSER

    def test_browser_navigate(self, router):
        result = router.classify_query("Browse to https://example.com and read it")
        assert result is AgenticSeekAgentType.BROWSER

    def test_file_find(self, router):
        result = router.classify_query("Find a file called report.pdf in my Downloads folder")
        assert result is AgenticSeekAgentType.FILE

    def test_file_create(self, router):
        result = router.classify_query("Create a new directory called projects")
        assert result is AgenticSeekAgentType.FILE

    def test_planner_complex(self, router):
        result = router.classify_query(
            "Plan a step by step workflow to organize my project files"
        )
        assert result is AgenticSeekAgentType.PLANNER

    def test_casual_greeting(self, router):
        result = router.classify_query("Hello, how are you?")
        assert result is AgenticSeekAgentType.CASUAL


# ===================================================================
# classify_query – heuristic fallbacks
# ===================================================================

class TestClassifyQueryHeuristics:
    """Verify structural heuristics when no keywords match."""

    def test_code_fence_triggers_coder(self, router):
        result = router.classify_query("Fix this:\n```\nx = 1\n```")
        assert result is AgenticSeekAgentType.CODER

    def test_url_triggers_browser(self, router):
        result = router.classify_query("Read this: https://example.com/page")
        assert result is AgenticSeekAgentType.BROWSER

    def test_file_path_triggers_file(self, router):
        result = router.classify_query("Check /home/user/notes.txt")
        assert result is AgenticSeekAgentType.FILE


# ===================================================================
# classify_query – edge cases
# ===================================================================

class TestClassifyQueryEdgeCases:
    """Edge cases: empty, whitespace, special characters."""

    def test_empty_string_returns_default(self, router):
        assert router.classify_query("") is AgenticSeekAgentType.CASUAL

    def test_whitespace_only_returns_default(self, router):
        assert router.classify_query("   ") is AgenticSeekAgentType.CASUAL

    def test_custom_default_agent(self):
        r = AgenticSeekRouter(default_agent=AgenticSeekAgentType.CODER)
        assert r.classify_query("Hey!") is AgenticSeekAgentType.CODER


# ===================================================================
# estimate_complexity
# ===================================================================

class TestEstimateComplexity:
    """Verify LOW vs HIGH complexity estimation."""

    def test_simple_prompt_is_low(self, router):
        assert router.estimate_complexity("Write a hello world program") == "LOW"

    def test_multi_step_is_high(self, router):
        query = (
            "First search the web for Python tutorials, "
            "then write a script, and finally test it"
        )
        assert router.estimate_complexity(query) == "HIGH"

    def test_empty_is_low(self, router):
        assert router.estimate_complexity("") == "LOW"

    def test_single_indicator_is_low(self, router):
        assert router.estimate_complexity("Do it step by step") == "LOW"

    def test_two_indicators_is_high(self, router):
        query = "First do step one, then do step two"
        assert router.estimate_complexity(query) == "HIGH"


# ===================================================================
# _score helper
# ===================================================================

class TestScoreHelper:
    def test_no_match_returns_zero(self):
        assert _score("hello world", frozenset({"foo", "bar"})) == 0

    def test_single_match(self):
        assert _score("hello world", frozenset({"hello"})) == 1

    def test_multiple_matches(self):
        assert _score("python code debug", frozenset({"python", "code", "debug"})) == 3
