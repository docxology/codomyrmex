"""Tests for ClaudeTaskMaster pure logic — no API calls.

Tests all data classes, enums, parsing logic, cost calculation,
message formatting, code extraction, usage tracking, and
initialization behavior of the claude_task_master module.

Methods that hit the Anthropic API are guarded by ANTHROPIC_API_KEY skipif.
"""

import os

import pytest

from codomyrmex.agents.ai_code_editing.claude_task_master import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_TOKENS,
    TASK_MASTER_PRICING,
    ClaudeTaskMaster,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def master_no_key():
    """ClaudeTaskMaster initialized explicitly with no API key."""
    saved = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        m = ClaudeTaskMaster(api_key=None)
        yield m
    finally:
        if saved is not None:
            os.environ["ANTHROPIC_API_KEY"] = saved


@pytest.fixture
def master_fake_key():
    """ClaudeTaskMaster initialized with a dummy key (never calls API)."""
    return ClaudeTaskMaster(api_key="sk-test-fake-key-for-unit-tests")


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestModuleConstants:
    """Validate module-level constants are sane."""

    def test_default_model_is_string(self):
        assert isinstance(DEFAULT_MODEL, str)
        assert "claude" in DEFAULT_MODEL.lower()

    def test_default_temperature_range(self):
        assert 0.0 <= DEFAULT_TEMPERATURE <= 2.0

    def test_max_tokens_positive(self):
        assert MAX_TOKENS > 0

    def test_pricing_dict_has_default_model(self):
        assert DEFAULT_MODEL in TASK_MASTER_PRICING

    def test_pricing_entries_have_input_and_output(self):
        for model, prices in TASK_MASTER_PRICING.items():
            assert "input" in prices, f"Missing 'input' price for {model}"
            assert "output" in prices, f"Missing 'output' price for {model}"
            assert prices["input"] > 0
            assert prices["output"] > 0


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTaskPriorityEnum:
    """TaskPriority enum values and membership."""

    def test_values(self):
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.CRITICAL.value == "critical"

    def test_member_count(self):
        assert len(TaskPriority) == 4

    def test_from_value(self):
        assert TaskPriority("low") is TaskPriority.LOW
        assert TaskPriority("critical") is TaskPriority.CRITICAL

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            TaskPriority("urgent")


@pytest.mark.unit
class TestTaskStatusEnum:
    """TaskStatus enum values and membership."""

    def test_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_member_count(self):
        assert len(TaskStatus) == 5

    def test_from_value(self):
        assert TaskStatus("failed") is TaskStatus.FAILED

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            TaskStatus("unknown")


# ---------------------------------------------------------------------------
# Task dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTaskDataclass:
    """Task dataclass creation and field defaults."""

    def test_minimal_creation(self):
        t = Task(description="Write tests")
        assert t.description == "Write tests"
        assert t.priority is TaskPriority.MEDIUM
        assert t.context is None
        assert t.dependencies == []
        assert t.timeout is None
        assert t.tags == []

    def test_full_creation(self):
        t = Task(
            description="Deploy service",
            priority=TaskPriority.CRITICAL,
            context="Production environment",
            dependencies=["build", "test"],
            timeout=300.0,
            tags=["deploy", "prod"],
        )
        assert t.priority is TaskPriority.CRITICAL
        assert t.context == "Production environment"
        assert len(t.dependencies) == 2
        assert t.timeout == 300.0
        assert "prod" in t.tags

    def test_mutable_defaults_are_independent(self):
        """Each Task instance must have its own list instances."""
        t1 = Task(description="A")
        t2 = Task(description="B")
        t1.dependencies.append("x")
        t1.tags.append("y")
        assert t1.dependencies != t2.dependencies
        assert t1.tags != t2.tags

    @pytest.mark.parametrize(
        "priority",
        [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH, TaskPriority.CRITICAL],
    )
    def test_all_priorities_accepted(self, priority):
        t = Task(description="test", priority=priority)
        assert t.priority is priority


# ---------------------------------------------------------------------------
# TaskResult dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTaskResultDataclass:
    """TaskResult dataclass creation and defaults."""

    def test_minimal_creation(self):
        r = TaskResult(
            task_id="task_1",
            status=TaskStatus.COMPLETED,
            result="done",
            execution_time=1.5,
            tokens_used=100,
        )
        assert r.task_id == "task_1"
        assert r.status is TaskStatus.COMPLETED
        assert r.result == "done"
        assert r.execution_time == 1.5
        assert r.tokens_used == 100
        assert r.cost_usd == 0.0
        assert r.error is None
        assert r.retries == 0

    def test_full_creation(self):
        r = TaskResult(
            task_id="task_99",
            status=TaskStatus.FAILED,
            result=None,
            execution_time=0.3,
            tokens_used=0,
            cost_usd=0.01,
            error="Rate limited",
            retries=3,
        )
        assert r.error == "Rate limited"
        assert r.retries == 3
        assert r.cost_usd == 0.01

    @pytest.mark.parametrize("status", list(TaskStatus))
    def test_all_statuses_accepted(self, status):
        r = TaskResult(
            task_id="t", status=status, result=None, execution_time=0, tokens_used=0,
        )
        assert r.status is status


# ---------------------------------------------------------------------------
# ClaudeTaskMaster.__init__
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClaudeTaskMasterInit:
    """Initialization, defaults, and API-key handling."""

    def test_defaults(self, master_fake_key):
        m = master_fake_key
        assert m.model == DEFAULT_MODEL
        assert m.max_retries == ClaudeTaskMaster.DEFAULT_MAX_RETRIES
        assert m._task_counter == 0
        assert m._total_cost == 0.0
        assert m._total_tokens == 0
        assert m._client is None

    def test_custom_model_and_retries(self):
        m = ClaudeTaskMaster(
            api_key="sk-test", model="claude-3-opus-20240229", max_retries=5,
        )
        assert m.model == "claude-3-opus-20240229"
        assert m.max_retries == 5

    def test_no_api_key_does_not_raise(self, master_no_key):
        """Init without key logs warning but does not raise."""
        assert master_no_key.api_key is None

    def test_get_client_raises_without_key(self, master_no_key):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            master_no_key._get_client()


# ---------------------------------------------------------------------------
# _calculate_cost
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCalculateCost:
    """Cost calculation for various models and token counts."""

    def test_zero_tokens(self, master_fake_key):
        assert master_fake_key._calculate_cost(0, 0) == 0.0

    def test_known_model_pricing(self):
        m = ClaudeTaskMaster(api_key="sk-test", model="claude-sonnet-4-20250514")
        # 1M input tokens @ $3, 1M output tokens @ $15 = $18
        cost = m._calculate_cost(1_000_000, 1_000_000)
        assert cost == 18.0

    def test_fractional_tokens(self):
        m = ClaudeTaskMaster(api_key="sk-test", model="claude-sonnet-4-20250514")
        # 1000 input @ $3/1M = $0.003, 500 output @ $15/1M = $0.0075
        cost = m._calculate_cost(1000, 500)
        assert abs(cost - 0.0105) < 1e-6

    def test_unknown_model_uses_default_pricing(self):
        m = ClaudeTaskMaster(api_key="sk-test", model="claude-future-99")
        # Default pricing: input $3/1M, output $15/1M
        cost = m._calculate_cost(1_000_000, 1_000_000)
        assert cost == 18.0

    @pytest.mark.parametrize(
        "model,expected_input_rate,expected_output_rate",
        [
            ("claude-sonnet-4-20250514", 3.00, 15.00),
            ("claude-3-5-haiku-20241022", 1.00, 5.00),
            ("claude-3-opus-20240229", 15.00, 75.00),
            ("claude-opus-4-5-20251101", 15.00, 75.00),
        ],
    )
    def test_model_specific_rates(self, model, expected_input_rate, expected_output_rate):
        m = ClaudeTaskMaster(api_key="sk-test", model=model)
        cost = m._calculate_cost(1_000_000, 1_000_000)
        expected = expected_input_rate + expected_output_rate
        assert abs(cost - expected) < 1e-6

    def test_result_is_rounded_to_six_decimals(self, master_fake_key):
        cost = master_fake_key._calculate_cost(1, 1)
        # Very tiny cost; ensure it has no more than 6 decimal places
        as_str = f"{cost:.10f}"
        # After 6th decimal, remainder should be zero
        assert float(as_str) == round(float(as_str), 6)


# ---------------------------------------------------------------------------
# _build_task_system_prompt / _build_task_message
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMessageBuilding:
    """System prompt and user message construction."""

    def test_system_prompt_is_nonempty_string(self, master_fake_key):
        prompt = master_fake_key._build_task_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 20
        assert "task master" in prompt.lower()

    def test_task_message_without_context(self, master_fake_key):
        msg = master_fake_key._build_task_message("Do the thing", None)
        assert "Task: Do the thing" in msg
        assert "Context" not in msg

    def test_task_message_with_context(self, master_fake_key):
        msg = master_fake_key._build_task_message("Do it", "Some context")
        assert "Context: Some context" in msg
        assert "Task: Do it" in msg


# ---------------------------------------------------------------------------
# _parse_subtasks
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParseSubtasks:
    """Subtask parsing from numbered and bulleted lists."""

    def test_numbered_dot_format(self, master_fake_key):
        text = "1. First task\n2. Second task\n3. Third task"
        result = master_fake_key._parse_subtasks(text)
        assert len(result) == 3
        assert result[0]["id"] == 1
        assert result[0]["description"] == "First task"
        assert result[0]["status"] == "pending"

    def test_numbered_paren_format(self, master_fake_key):
        text = "1) Alpha\n2) Beta"
        result = master_fake_key._parse_subtasks(text)
        assert len(result) == 2
        assert result[0]["description"] == "Alpha"
        assert result[1]["description"] == "Beta"

    def test_bullet_dash_format(self, master_fake_key):
        text = "- First bullet\n- Second bullet"
        result = master_fake_key._parse_subtasks(text)
        assert len(result) == 2
        assert result[0]["description"] == "First bullet"

    def test_bullet_asterisk_format(self, master_fake_key):
        text = "* Star one\n* Star two"
        result = master_fake_key._parse_subtasks(text)
        assert len(result) == 2

    def test_empty_input(self, master_fake_key):
        result = master_fake_key._parse_subtasks("")
        assert result == []

    def test_no_matching_lines(self, master_fake_key):
        text = "This is just a paragraph.\nNo numbered items here."
        result = master_fake_key._parse_subtasks(text)
        assert result == []

    def test_mixed_formats(self, master_fake_key):
        text = "1. Numbered\n- Bullet\n2. Another number"
        result = master_fake_key._parse_subtasks(text)
        assert len(result) == 3

    def test_dependencies_extracted(self, master_fake_key):
        text = "1. Setup environment\n2. Write code [Depends on: 1]\n3. Test code [Depends on: 1, 2]"
        result = master_fake_key._parse_subtasks(text, include_dependencies=True)
        assert len(result) == 3
        # First task has no dependencies
        assert "dependencies" not in result[0]
        # Second task depends on 1
        assert result[1]["dependencies"] == ["1"]
        # Third depends on 1, 2
        assert result[2]["dependencies"] == ["1", "2"]
        # Dependency marker should be stripped from description
        assert "[Depends on" not in result[1]["description"]
        assert "[Depends on" not in result[2]["description"]

    def test_dependencies_not_extracted_when_flag_false(self, master_fake_key):
        text = "1. Write code [Depends on: setup]"
        result = master_fake_key._parse_subtasks(text, include_dependencies=False)
        assert len(result) == 1
        # The dependency text stays in description because flag is False
        assert "dependencies" not in result[0]
        assert "[Depends on" in result[0]["description"]

    def test_whitespace_handling(self, master_fake_key):
        text = "  1. Indented item  \n  2.   Extra spaces  "
        result = master_fake_key._parse_subtasks(text)
        assert len(result) == 2
        # Descriptions should be stripped
        assert result[0]["description"] == "Indented item"
        assert result[1]["description"] == "Extra spaces"


# ---------------------------------------------------------------------------
# _parse_analysis
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParseAnalysis:
    """Analysis text parsing for complexity extraction."""

    def test_high_complexity(self, master_fake_key):
        text = "Complexity Assessment: HIGH\nThis is a complex task."
        parsed = master_fake_key._parse_analysis(text)
        assert parsed["complexity"] == "high"

    def test_medium_complexity(self, master_fake_key):
        text = "The complexity is medium given the requirements."
        parsed = master_fake_key._parse_analysis(text)
        assert parsed["complexity"] == "medium"

    def test_low_complexity(self, master_fake_key):
        text = "Complexity: Low. Simple task."
        parsed = master_fake_key._parse_analysis(text)
        assert parsed["complexity"] == "low"

    def test_no_complexity_detected(self, master_fake_key):
        text = "This task requires Python knowledge."
        parsed = master_fake_key._parse_analysis(text)
        assert parsed["complexity"] is None

    def test_parsed_structure_has_expected_keys(self, master_fake_key):
        parsed = master_fake_key._parse_analysis("Some analysis text.")
        expected_keys = {"complexity", "effort", "skills", "risks", "approach"}
        assert set(parsed.keys()) == expected_keys

    def test_default_values(self, master_fake_key):
        parsed = master_fake_key._parse_analysis("")
        assert parsed["effort"] is None
        assert parsed["skills"] == []
        assert parsed["risks"] == []
        assert parsed["approach"] is None


# ---------------------------------------------------------------------------
# _extract_code
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestExtractCode:
    """Code extraction from markdown-formatted responses."""

    def test_language_specific_block(self, master_fake_key):
        response = "Here is the code:\n```python\ndef hello():\n    return 'hi'\n```\nDone."
        code = master_fake_key._extract_code(response, "python")
        assert "def hello():" in code
        assert "return 'hi'" in code
        assert "```" not in code

    def test_generic_code_block(self, master_fake_key):
        response = "Code:\n```\nsome code here\n```"
        code = master_fake_key._extract_code(response, "rust")
        assert code == "some code here"

    def test_no_code_block_returns_stripped(self, master_fake_key):
        response = "  Just plain text without code blocks  "
        code = master_fake_key._extract_code(response, "python")
        assert code == "Just plain text without code blocks"

    def test_multiple_blocks_extracts_first_matching(self, master_fake_key):
        response = (
            "```python\nfirst_block()\n```\n\n"
            "```python\nsecond_block()\n```"
        )
        code = master_fake_key._extract_code(response, "python")
        assert "first_block()" in code

    def test_case_insensitive_language_match(self, master_fake_key):
        response = "```Python\ncode_here()\n```"
        code = master_fake_key._extract_code(response, "python")
        assert "code_here()" in code

    @pytest.mark.parametrize(
        "lang", ["python", "javascript", "rust", "go", "typescript"],
    )
    def test_various_languages(self, master_fake_key, lang):
        response = f"```{lang}\n// code for {lang}\n```"
        code = master_fake_key._extract_code(response, lang)
        assert f"// code for {lang}" in code


# ---------------------------------------------------------------------------
# Usage stats
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestUsageStats:
    """Usage statistics tracking and reset."""

    def test_initial_stats(self, master_fake_key):
        stats = master_fake_key.get_usage_stats()
        assert stats["total_tasks"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_cost_usd"] == 0.0
        assert stats["model"] == DEFAULT_MODEL

    def test_reset_clears_counters(self, master_fake_key):
        m = master_fake_key
        m._task_counter = 5
        m._total_tokens = 999
        m._total_cost = 1.23
        m.reset_usage_stats()
        stats = m.get_usage_stats()
        assert stats["total_tasks"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_cost_usd"] == 0.0

    def test_stats_reflect_internal_state(self, master_fake_key):
        m = master_fake_key
        m._task_counter = 3
        m._total_tokens = 5000
        m._total_cost = 0.123456
        stats = m.get_usage_stats()
        assert stats["total_tasks"] == 3
        assert stats["total_tokens"] == 5000
        assert stats["total_cost_usd"] == 0.123456

    def test_cost_rounding_in_stats(self, master_fake_key):
        m = master_fake_key
        m._total_cost = 0.12345678901
        stats = m.get_usage_stats()
        # get_usage_stats rounds to 6 decimals
        assert stats["total_cost_usd"] == 0.123457


# ---------------------------------------------------------------------------
# is_available
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsAvailable:
    """Availability checks without hitting the network."""

    def test_not_available_without_key(self, master_no_key):
        assert master_no_key.is_available() is False

    def test_available_with_fake_key(self, master_fake_key):
        # With a key present, _get_client() will construct the Anthropic object,
        # so is_available returns True as long as the anthropic package is installed.
        assert master_fake_key.is_available() is True


# ---------------------------------------------------------------------------
# Retry configuration constants
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRetryConstants:
    """Class-level retry configuration constants."""

    def test_default_max_retries(self):
        assert ClaudeTaskMaster.DEFAULT_MAX_RETRIES == 3

    def test_default_initial_delay(self):
        assert ClaudeTaskMaster.DEFAULT_INITIAL_DELAY == 1.0

    def test_default_backoff_factor(self):
        assert ClaudeTaskMaster.DEFAULT_BACKOFF_FACTOR == 2.0


# ---------------------------------------------------------------------------
# API-dependent methods (skipped without key)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAPIMethodsSkippedWithoutKey:
    """Methods that require a live API key -- skipped by default.

    The skip check is performed at test-execution time (not collection time)
    so that changes to ANTHROPIC_API_KEY between collection and execution are
    handled correctly.
    """

    @pytest.fixture(autouse=True)
    def require_api_key(self):
        """Skip all tests in this class when ANTHROPIC_API_KEY is absent."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

    def test_execute_task_returns_dict(self):
        m = ClaudeTaskMaster()
        result = m.execute_task("Say hello in one word")
        assert isinstance(result, dict)
        assert "task_id" in result
        assert result["status"] in ("completed", "failed")

    def test_decompose_task_returns_subtasks(self):
        m = ClaudeTaskMaster()
        result = m.decompose_task("Build a REST API", max_subtasks=3)
        assert isinstance(result, dict)
        assert "subtasks" in result

    def test_analyze_task_returns_analysis(self):
        m = ClaudeTaskMaster()
        result = m.analyze_task("Refactor the payment module")
        assert isinstance(result, dict)
        assert "analysis" in result

    def test_plan_workflow_returns_plan(self):
        m = ClaudeTaskMaster()
        result = m.plan_workflow("Deploy microservices")
        assert isinstance(result, dict)
        assert "plan" in result

    def test_generate_code_returns_code(self):
        m = ClaudeTaskMaster()
        result = m.generate_code("A function that adds two numbers", language="python")
        assert isinstance(result, dict)
        assert "code" in result
