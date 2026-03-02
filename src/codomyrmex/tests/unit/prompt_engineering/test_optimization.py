"""
Unit tests for prompt_engineering.optimization — Zero-Mock compliant.

Covers: OptimizationStrategy, OptimizationResult (token_reduction_estimate,
to_dict), PromptOptimizer (optimize, bulk_optimize, available_strategies,
set_few_shot_examples, _optimize_concise, _optimize_detailed,
_optimize_chain_of_thought, _optimize_few_shot).
"""

import pytest

from codomyrmex.prompt_engineering.optimization import (
    OptimizationResult,
    OptimizationStrategy,
    PromptOptimizer,
)
from codomyrmex.prompt_engineering.templates import PromptTemplate

# ── Helpers ───────────────────────────────────────────────────────────


def _tmpl(text: str, name: str = "test") -> PromptTemplate:
    """Create a PromptTemplate with the given text."""
    return PromptTemplate(name=name, template_str=text)


# ── OptimizationStrategy enum ─────────────────────────────────────────


@pytest.mark.unit
class TestOptimizationStrategy:
    def test_values(self):
        assert OptimizationStrategy.CONCISE.value == "concise"
        assert OptimizationStrategy.DETAILED.value == "detailed"
        assert OptimizationStrategy.CHAIN_OF_THOUGHT.value == "chain_of_thought"
        assert OptimizationStrategy.FEW_SHOT.value == "few_shot"

    def test_four_strategies(self):
        assert len(list(OptimizationStrategy)) == 4


# ── OptimizationResult ────────────────────────────────────────────────


@pytest.mark.unit
class TestOptimizationResult:
    def _make_result(self, original_text: str, optimized_text: str) -> OptimizationResult:
        return OptimizationResult(
            original=_tmpl(original_text, "orig"),
            optimized=_tmpl(optimized_text, "opt"),
            strategy=OptimizationStrategy.CONCISE,
        )

    def test_token_reduction_estimate_shorter(self):
        r = self._make_result("one two three four", "one two")
        # 2/4 = 0.5
        assert r.token_reduction_estimate == pytest.approx(0.5)

    def test_token_reduction_estimate_same_length(self):
        r = self._make_result("one two", "one two")
        assert r.token_reduction_estimate == 1.0

    def test_token_reduction_estimate_longer(self):
        r = self._make_result("short", "this is much longer now")
        assert r.token_reduction_estimate > 1.0

    def test_token_reduction_empty_original(self):
        r = self._make_result("", "some text")
        assert r.token_reduction_estimate == 1.0

    def test_to_dict_keys(self):
        r = self._make_result("hello world", "hello")
        d = r.to_dict()
        assert "original" in d
        assert "optimized" in d
        assert "strategy" in d
        assert "changes" in d
        assert "token_reduction_estimate" in d
        assert "metadata" in d

    def test_to_dict_strategy_value(self):
        r = self._make_result("text", "text")
        d = r.to_dict()
        assert d["strategy"] == "concise"

    def test_to_dict_changes_list(self):
        r = OptimizationResult(
            original=_tmpl("x"),
            optimized=_tmpl("x"),
            strategy=OptimizationStrategy.CONCISE,
            changes=["did something"],
        )
        d = r.to_dict()
        assert d["changes"] == ["did something"]

    def test_to_dict_token_estimate_is_float(self):
        r = self._make_result("a b c", "a b")
        d = r.to_dict()
        assert isinstance(d["token_reduction_estimate"], float)


# ── PromptOptimizer — available_strategies ────────────────────────────


@pytest.mark.unit
class TestAvailableStrategies:
    def test_returns_list(self):
        opt = PromptOptimizer()
        strategies = opt.available_strategies()
        assert isinstance(strategies, list)

    def test_length_is_four(self):
        opt = PromptOptimizer()
        assert len(opt.available_strategies()) == 4

    def test_sorted(self):
        opt = PromptOptimizer()
        strats = opt.available_strategies()
        assert strats == sorted(strats)

    def test_contains_all_values(self):
        opt = PromptOptimizer()
        strats = set(opt.available_strategies())
        assert "concise" in strats
        assert "detailed" in strats
        assert "chain_of_thought" in strats
        assert "few_shot" in strats


# ── PromptOptimizer — optimize (CONCISE) ─────────────────────────────


@pytest.mark.unit
class TestOptimizeConcise:
    def test_returns_optimization_result(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Please do this."), OptimizationStrategy.CONCISE)
        assert isinstance(r, OptimizationResult)

    def test_removes_please(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Please do this."), OptimizationStrategy.CONCISE)
        assert "please" not in r.optimized.template_str.lower()

    def test_removes_kindly(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Kindly explain this."), OptimizationStrategy.CONCISE)
        assert "kindly" not in r.optimized.template_str.lower()

    def test_removes_i_would_like_you_to(self):
        opt = PromptOptimizer()
        r = opt.optimize(
            _tmpl("I would like you to explain this."), OptimizationStrategy.CONCISE
        )
        assert "I would like you to" not in r.optimized.template_str

    def test_collapses_multiple_blank_lines(self):
        opt = PromptOptimizer()
        text = "line1\n\n\n\nline2"
        r = opt.optimize(_tmpl(text), OptimizationStrategy.CONCISE)
        assert "\n\n\n" not in r.optimized.template_str

    def test_no_changes_adds_message(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Analyze the data."), OptimizationStrategy.CONCISE)
        # No filler patterns present → should produce "No concise optimizations applicable"
        assert len(r.changes) >= 1

    def test_optimized_name_contains_strategy(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this.", "my_tmpl"), OptimizationStrategy.CONCISE)
        assert "concise" in r.optimized.name

    def test_source_template_in_metadata(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this.", "source_tmpl"), OptimizationStrategy.CONCISE)
        assert r.optimized.metadata["source_template"] == "source_tmpl"

    def test_strategy_in_optimized_metadata(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this."), OptimizationStrategy.CONCISE)
        assert r.optimized.metadata["optimization_strategy"] == "concise"


# ── PromptOptimizer — optimize (DETAILED) ────────────────────────────


@pytest.mark.unit
class TestOptimizeDetailed:
    def test_adds_role_section(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this task."), OptimizationStrategy.DETAILED)
        assert "## Role" in r.optimized.template_str

    def test_adds_task_section(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this task."), OptimizationStrategy.DETAILED)
        assert "## Task" in r.optimized.template_str

    def test_adds_constraints_section(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this task."), OptimizationStrategy.DETAILED)
        assert "## Constraints" in r.optimized.template_str

    def test_adds_output_format_section(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this task."), OptimizationStrategy.DETAILED)
        assert "## Output Format" in r.optimized.template_str

    def test_original_text_preserved_in_task(self):
        opt = PromptOptimizer()
        original_text = "Analyze this data carefully."
        r = opt.optimize(_tmpl(original_text), OptimizationStrategy.DETAILED)
        assert original_text in r.optimized.template_str

    def test_no_role_if_already_present(self):
        opt = PromptOptimizer()
        r = opt.optimize(
            _tmpl("You are an expert. Do this."), OptimizationStrategy.DETAILED
        )
        changes = " ".join(r.changes)
        assert "role" not in changes.lower()

    def test_changes_non_empty(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do this."), OptimizationStrategy.DETAILED)
        assert len(r.changes) > 0


# ── PromptOptimizer — optimize (CHAIN_OF_THOUGHT) ─────────────────────


@pytest.mark.unit
class TestOptimizeChainOfThought:
    def test_adds_step_by_step_preamble(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Solve this."), OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert "step-by-step" in r.optimized.template_str.lower()

    def test_adds_reasoning_scaffold(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Solve this."), OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert "reasoning process" in r.optimized.template_str.lower()

    def test_adds_answer_delimiter(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Solve this."), OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert "ANSWER:" in r.optimized.template_str

    def test_original_text_preserved(self):
        opt = PromptOptimizer()
        original = "What is 2 + 2?"
        r = opt.optimize(_tmpl(original), OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert original in r.optimized.template_str

    def test_no_duplicate_preamble_if_present(self):
        opt = PromptOptimizer()
        # Text already contains "think step by step"
        r = opt.optimize(
            _tmpl("Think step by step to solve this."),
            OptimizationStrategy.CHAIN_OF_THOUGHT,
        )
        changes = " ".join(r.changes)
        assert "preamble" not in changes.lower()

    def test_changes_non_empty(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Analyze this."), OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert len(r.changes) > 0


# ── PromptOptimizer — optimize (FEW_SHOT) ────────────────────────────


@pytest.mark.unit
class TestOptimizeFewShot:
    def test_no_examples_adds_placeholder(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Translate this."), OptimizationStrategy.FEW_SHOT)
        assert "No examples provided" in r.optimized.template_str

    def test_with_examples_kwarg(self):
        opt = PromptOptimizer()
        examples = [{"input": "cat", "output": "gato"}]
        r = opt.optimize(
            _tmpl("Translate to Spanish."),
            OptimizationStrategy.FEW_SHOT,
            examples=examples,
        )
        assert "cat" in r.optimized.template_str
        assert "gato" in r.optimized.template_str

    def test_set_few_shot_examples(self):
        opt = PromptOptimizer()
        opt.set_few_shot_examples([{"input": "hello", "output": "hola"}])
        r = opt.optimize(_tmpl("Translate."), OptimizationStrategy.FEW_SHOT)
        assert "hello" in r.optimized.template_str
        assert "hola" in r.optimized.template_str

    def test_multiple_examples_numbered(self):
        opt = PromptOptimizer()
        examples = [
            {"input": "a", "output": "A"},
            {"input": "b", "output": "B"},
        ]
        r = opt.optimize(
            _tmpl("Convert."), OptimizationStrategy.FEW_SHOT, examples=examples
        )
        assert "Example 1" in r.optimized.template_str
        assert "Example 2" in r.optimized.template_str

    def test_original_prompt_appended_after_examples(self):
        opt = PromptOptimizer()
        opt.set_few_shot_examples([{"input": "x", "output": "y"}])
        original_text = "Now do the thing."
        r = opt.optimize(_tmpl(original_text), OptimizationStrategy.FEW_SHOT)
        assert original_text in r.optimized.template_str

    def test_changes_non_empty(self):
        opt = PromptOptimizer()
        r = opt.optimize(_tmpl("Do it."), OptimizationStrategy.FEW_SHOT)
        assert len(r.changes) > 0


# ── PromptOptimizer — bulk_optimize ──────────────────────────────────


@pytest.mark.unit
class TestBulkOptimize:
    def test_bulk_returns_list(self):
        opt = PromptOptimizer()
        templates = [_tmpl("Please do A."), _tmpl("Please do B.")]
        results = opt.bulk_optimize(templates, OptimizationStrategy.CONCISE)
        assert isinstance(results, list)
        assert len(results) == 2

    def test_bulk_all_same_strategy(self):
        opt = PromptOptimizer()
        templates = [_tmpl("Task 1"), _tmpl("Task 2"), _tmpl("Task 3")]
        results = opt.bulk_optimize(templates, OptimizationStrategy.DETAILED)
        for r in results:
            assert r.strategy == OptimizationStrategy.DETAILED

    def test_bulk_empty_list(self):
        opt = PromptOptimizer()
        results = opt.bulk_optimize([], OptimizationStrategy.CONCISE)
        assert results == []

    def test_bulk_preserves_order(self):
        opt = PromptOptimizer()
        templates = [_tmpl(f"Task {i}", f"t{i}") for i in range(5)]
        results = opt.bulk_optimize(templates, OptimizationStrategy.CONCISE)
        for i, r in enumerate(results):
            assert r.original.name == f"t{i}"
