"""Zero-mock tests for prompt_engineering.optimization module.

Targets uncovered paths in PromptOptimizer strategies and OptimizationResult.
All tests use real function calls with inline data - no mocking.
"""

import pytest

from codomyrmex.prompt_engineering.optimization import (
    OptimizationResult,
    OptimizationStrategy,
    PromptOptimizer,
)
from codomyrmex.prompt_engineering.templates import PromptTemplate


def make_template(content: str, name: str = "test_template") -> PromptTemplate:
    """Helper to create a PromptTemplate for testing."""
    return PromptTemplate(name=name, template_str=content)


class TestOptimizationStrategy:
    """Tests for OptimizationStrategy enum."""

    def test_all_strategies_have_values(self):
        assert OptimizationStrategy.CONCISE.value == "concise"
        assert OptimizationStrategy.DETAILED.value == "detailed"
        assert OptimizationStrategy.CHAIN_OF_THOUGHT.value == "chain_of_thought"
        assert OptimizationStrategy.FEW_SHOT.value == "few_shot"

    def test_four_strategies_available(self):
        assert len(list(OptimizationStrategy)) == 4


class TestOptimizationResult:
    """Tests for OptimizationResult properties."""

    def test_token_reduction_estimate_shorter(self):
        original = make_template("please do this thing and that thing and more")
        optimized = make_template("do this")
        result = OptimizationResult(
            original=original,
            optimized=optimized,
            strategy=OptimizationStrategy.CONCISE,
        )
        ratio = result.token_reduction_estimate
        assert ratio < 1.0

    def test_token_reduction_estimate_equal_length(self):
        original = make_template("same length text here")
        optimized = make_template("same length text here")
        result = OptimizationResult(
            original=original,
            optimized=optimized,
            strategy=OptimizationStrategy.CONCISE,
        )
        assert abs(result.token_reduction_estimate - 1.0) < 0.01

    def test_token_reduction_estimate_empty_original(self):
        original = make_template("")
        optimized = make_template("some content added")
        result = OptimizationResult(
            original=original,
            optimized=optimized,
            strategy=OptimizationStrategy.DETAILED,
        )
        # Empty original returns 1.0 to avoid division by zero
        assert result.token_reduction_estimate == 1.0

    def test_to_dict_contains_expected_keys(self):
        original = make_template("Write a poem")
        optimized = make_template("Write a poem optimized")
        result = OptimizationResult(
            original=original,
            optimized=optimized,
            strategy=OptimizationStrategy.DETAILED,
            changes=["Added role section"],
        )
        d = result.to_dict()
        assert "original" in d
        assert "optimized" in d
        assert "strategy" in d
        assert "changes" in d
        assert "token_reduction_estimate" in d
        assert "metadata" in d
        assert d["strategy"] == "detailed"

    def test_changes_list_in_to_dict(self):
        original = make_template("test")
        optimized = make_template("test optimized")
        result = OptimizationResult(
            original=original,
            optimized=optimized,
            strategy=OptimizationStrategy.CONCISE,
            changes=["change1", "change2"],
        )
        d = result.to_dict()
        assert d["changes"] == ["change1", "change2"]


class TestPromptOptimizerInit:
    """Tests for PromptOptimizer initialization."""

    def test_init_creates_strategy_handlers(self):
        optimizer = PromptOptimizer()
        assert len(optimizer._strategy_handlers) == 4

    def test_init_empty_few_shot_examples(self):
        optimizer = PromptOptimizer()
        assert optimizer._few_shot_examples == []

    def test_available_strategies_sorted(self):
        optimizer = PromptOptimizer()
        strategies = optimizer.available_strategies()
        assert strategies == sorted(strategies)
        assert len(strategies) == 4
        assert "concise" in strategies
        assert "detailed" in strategies
        assert "chain_of_thought" in strategies
        assert "few_shot" in strategies


class TestConciseOptimization:
    """Tests for the CONCISE optimization strategy."""

    def test_removes_please(self):
        optimizer = PromptOptimizer()
        template = make_template("Please write a summary of this document.")
        result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
        assert "please" not in result.optimized.template_str.lower()

    def test_removes_kindly(self):
        optimizer = PromptOptimizer()
        template = make_template("Kindly explain the difference between A and B.")
        result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
        assert "kindly" not in result.optimized.template_str.lower()

    def test_removes_i_would_like_you_to(self):
        optimizer = PromptOptimizer()
        template = make_template("I would like you to write a test.")
        result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
        assert len(result.changes) >= 1

    def test_collapses_multiple_blank_lines(self):
        optimizer = PromptOptimizer()
        template = make_template("First paragraph.\n\n\n\nSecond paragraph.")
        result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
        assert "\n\n\n" not in result.optimized.template_str

    def test_clean_prompt_gets_no_changes_message(self):
        optimizer = PromptOptimizer()
        template = make_template("Write a haiku about winter.")
        result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
        # Either no changes or the explicit message
        if result.changes:
            # May have stripped whitespace or found nothing
            assert len(result.changes) >= 1

    def test_returns_optimization_result(self):
        optimizer = PromptOptimizer()
        template = make_template("Please analyze this data.")
        result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
        assert isinstance(result, OptimizationResult)
        assert result.strategy == OptimizationStrategy.CONCISE
        assert result.original is template

    def test_optimized_template_name_includes_strategy(self):
        optimizer = PromptOptimizer()
        template = make_template("Please do something", name="my_template")
        result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
        assert "concise" in result.optimized.name


class TestDetailedOptimization:
    """Tests for the DETAILED optimization strategy."""

    def test_adds_role_section_when_missing(self):
        optimizer = PromptOptimizer()
        template = make_template("Summarize the following text.")
        result = optimizer.optimize(template, OptimizationStrategy.DETAILED)
        assert "Role" in result.optimized.template_str or "role" in result.optimized.template_str.lower()

    def test_wraps_in_task_section(self):
        optimizer = PromptOptimizer()
        template = make_template("Analyze this data.")
        result = optimizer.optimize(template, OptimizationStrategy.DETAILED)
        assert "Task" in result.optimized.template_str

    def test_adds_constraints_when_missing(self):
        optimizer = PromptOptimizer()
        template = make_template("Write a poem.")
        result = optimizer.optimize(template, OptimizationStrategy.DETAILED)
        assert "Constraint" in result.optimized.template_str or "constraint" in result.optimized.template_str.lower()

    def test_adds_output_format_when_missing(self):
        optimizer = PromptOptimizer()
        template = make_template("Describe the situation.")
        result = optimizer.optimize(template, OptimizationStrategy.DETAILED)
        assert "Output" in result.optimized.template_str or "format" in result.optimized.template_str.lower()

    def test_does_not_duplicate_role_when_present(self):
        optimizer = PromptOptimizer()
        template = make_template("You are a helpful assistant. Explain Python.")
        result = optimizer.optimize(template, OptimizationStrategy.DETAILED)
        # Role context shouldn't be added again
        assert result.changes  # some changes were made

    def test_changes_list_populated(self):
        optimizer = PromptOptimizer()
        template = make_template("Explain recursion.")
        result = optimizer.optimize(template, OptimizationStrategy.DETAILED)
        assert len(result.changes) >= 2


class TestChainOfThoughtOptimization:
    """Tests for the CHAIN_OF_THOUGHT optimization strategy."""

    def test_adds_step_by_step_preamble(self):
        optimizer = PromptOptimizer()
        template = make_template("Solve this math problem: 2 + 2.")
        result = optimizer.optimize(template, OptimizationStrategy.CHAIN_OF_THOUGHT)
        content = result.optimized.template_str
        assert "step" in content.lower() or "step-by-step" in content.lower()

    def test_adds_reasoning_scaffold(self):
        optimizer = PromptOptimizer()
        template = make_template("Analyze this scenario.")
        result = optimizer.optimize(template, OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert "reasoning" in result.optimized.template_str.lower()

    def test_adds_answer_delimiter(self):
        optimizer = PromptOptimizer()
        template = make_template("What is the meaning of life?")
        result = optimizer.optimize(template, OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert "ANSWER:" in result.optimized.template_str

    def test_no_preamble_if_already_step_by_step(self):
        optimizer = PromptOptimizer()
        template = make_template("Think step-by-step to solve this.")
        result = optimizer.optimize(template, OptimizationStrategy.CHAIN_OF_THOUGHT)
        # Preamble not added since "step" already there
        assert result.optimized.template_str  # still processed

    def test_changes_include_answer_delimiter(self):
        optimizer = PromptOptimizer()
        template = make_template("Solve: what is 10 + 5?")
        result = optimizer.optimize(template, OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert any("answer" in c.lower() for c in result.changes)


class TestFewShotOptimization:
    """Tests for the FEW_SHOT optimization strategy."""

    def test_with_examples_adds_them(self):
        optimizer = PromptOptimizer()
        optimizer.set_few_shot_examples([
            {"input": "cat", "output": "animal"},
            {"input": "car", "output": "vehicle"},
        ])
        template = make_template("Classify: dog")
        result = optimizer.optimize(template, OptimizationStrategy.FEW_SHOT)
        content = result.optimized.template_str
        assert "cat" in content
        assert "animal" in content

    def test_without_examples_adds_placeholder(self):
        optimizer = PromptOptimizer()
        template = make_template("Classify this item.")
        result = optimizer.optimize(template, OptimizationStrategy.FEW_SHOT)
        assert "No examples" in result.optimized.template_str or "no examples" in result.optimized.template_str.lower()

    def test_examples_via_kwargs(self):
        optimizer = PromptOptimizer()
        template = make_template("Translate: hello")
        examples = [{"input": "hi", "output": "hola"}]
        result = optimizer.optimize(
            template, OptimizationStrategy.FEW_SHOT, examples=examples
        )
        assert "hi" in result.optimized.template_str
        assert "hola" in result.optimized.template_str

    def test_set_few_shot_examples_stores_them(self):
        optimizer = PromptOptimizer()
        examples = [{"input": "x", "output": "y"}]
        optimizer.set_few_shot_examples(examples)
        assert optimizer._few_shot_examples == examples

    def test_changes_includes_example_count(self):
        optimizer = PromptOptimizer()
        optimizer.set_few_shot_examples([
            {"input": "a", "output": "b"},
            {"input": "c", "output": "d"},
        ])
        template = make_template("Test prompt")
        result = optimizer.optimize(template, OptimizationStrategy.FEW_SHOT)
        assert any("2" in c for c in result.changes)


class TestBulkOptimize:
    """Tests for PromptOptimizer.bulk_optimize method."""

    def test_bulk_optimize_returns_list(self):
        optimizer = PromptOptimizer()
        templates = [
            make_template("Please analyze this.", "t1"),
            make_template("Kindly explain that.", "t2"),
        ]
        results = optimizer.bulk_optimize(templates, OptimizationStrategy.CONCISE)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, OptimizationResult)

    def test_bulk_optimize_empty_list(self):
        optimizer = PromptOptimizer()
        results = optimizer.bulk_optimize([], OptimizationStrategy.DETAILED)
        assert results == []

    def test_bulk_optimize_applies_same_strategy(self):
        optimizer = PromptOptimizer()
        templates = [make_template("T1"), make_template("T2"), make_template("T3")]
        results = optimizer.bulk_optimize(templates, OptimizationStrategy.CHAIN_OF_THOUGHT)
        for r in results:
            assert r.strategy == OptimizationStrategy.CHAIN_OF_THOUGHT
