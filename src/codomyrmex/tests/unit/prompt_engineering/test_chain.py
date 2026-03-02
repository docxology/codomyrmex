"""Zero-Mock tests for prompt optimization chain construction.

Tests for PromptOptimizer strategies (concise, detailed, chain_of_thought,
few_shot), OptimizationResult properties, bulk optimization, and the
strategy-based transformation pipeline.
"""

import pytest

try:
    from codomyrmex.prompt_engineering.optimization import (
        OptimizationResult,
        OptimizationStrategy,
        PromptOptimizer,
    )
    from codomyrmex.prompt_engineering.templates import PromptTemplate

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("prompt_engineering.optimization not available", allow_module_level=True)


@pytest.mark.unit
class TestOptimizationStrategies:
    """Tests for individual optimization strategy transformations."""

    def test_concise_removes_filler(self):
        """Concise strategy should remove filler phrases like 'please'."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(
            name="verbose",
            template_str="I would like you to please explain {topic} in detail",
        )
        result = optimizer.optimize(t, OptimizationStrategy.CONCISE)
        assert isinstance(result, OptimizationResult)
        assert result.strategy == OptimizationStrategy.CONCISE
        assert len(result.changes) > 0
        # "please" or "I would like you to" should be removed
        optimized_lower = result.optimized.template_str.lower()
        assert "please" not in optimized_lower or "i would like you to" not in optimized_lower

    def test_concise_collapses_blank_lines(self):
        """Concise strategy should collapse multiple blank lines."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(
            name="spaced",
            template_str="Line one\n\n\n\n\nLine two",
        )
        result = optimizer.optimize(t, OptimizationStrategy.CONCISE)
        # Should have at most 2 consecutive newlines
        assert "\n\n\n" not in result.optimized.template_str

    def test_detailed_adds_task_section(self):
        """Detailed strategy should wrap prompt in a Task section."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="simple", template_str="Explain {topic}")
        result = optimizer.optimize(t, OptimizationStrategy.DETAILED)
        assert "## Task" in result.optimized.template_str

    def test_detailed_adds_role_section(self):
        """Detailed strategy should add Role section when not present."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Explain {topic}")
        result = optimizer.optimize(t, OptimizationStrategy.DETAILED)
        assert "## Role" in result.optimized.template_str

    def test_detailed_skips_role_if_present(self):
        """Detailed strategy should not add Role if already in prompt."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="You are a coding assistant. Explain {topic}")
        result = optimizer.optimize(t, OptimizationStrategy.DETAILED)
        # Should NOT have a separate "## Role" section since "You are" is already present
        assert result.optimized.template_str.count("## Role") == 0

    def test_chain_of_thought_adds_step_by_step(self):
        """Chain-of-thought should add step-by-step reasoning scaffold."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="solve", template_str="Solve {problem}")
        result = optimizer.optimize(t, OptimizationStrategy.CHAIN_OF_THOUGHT)
        lower = result.optimized.template_str.lower()
        assert "step" in lower
        assert "ANSWER:" in result.optimized.template_str

    def test_chain_of_thought_adds_reasoning_scaffold(self):
        """Chain-of-thought should add the 5-step reasoning framework."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Analyze {data}")
        result = optimizer.optimize(t, OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert "reasoning process" in result.optimized.template_str.lower()

    def test_few_shot_with_examples(self):
        """Few-shot should inject examples into the prompt."""
        optimizer = PromptOptimizer()
        optimizer.set_few_shot_examples([
            {"input": "2+2", "output": "4"},
            {"input": "3*3", "output": "9"},
        ])
        t = PromptTemplate(name="math", template_str="Calculate {expression}")
        result = optimizer.optimize(t, OptimizationStrategy.FEW_SHOT)
        assert "Example 1" in result.optimized.template_str
        assert "Example 2" in result.optimized.template_str

    def test_few_shot_without_examples(self):
        """Few-shot without examples should add placeholder note."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Do {task}")
        result = optimizer.optimize(t, OptimizationStrategy.FEW_SHOT)
        assert "No examples" in result.optimized.template_str

    def test_few_shot_via_kwargs(self):
        """Few-shot should accept examples via kwargs."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Translate {text}")
        examples = [{"input": "hello", "output": "hola"}]
        result = optimizer.optimize(t, OptimizationStrategy.FEW_SHOT, examples=examples)
        assert "Example 1" in result.optimized.template_str


@pytest.mark.unit
class TestOptimizationResult:
    """Tests for OptimizationResult properties and serialization."""

    def _make_result(self):
        optimizer = PromptOptimizer()
        t = PromptTemplate(
            name="verbose",
            template_str="I would like you to kindly please explain {topic}",
        )
        return optimizer.optimize(t, OptimizationStrategy.CONCISE)

    def test_token_reduction_estimate(self):
        """token_reduction_estimate should return a float ratio."""
        result = self._make_result()
        estimate = result.token_reduction_estimate
        assert isinstance(estimate, float)
        assert estimate > 0

    def test_token_reduction_for_concise(self):
        """Concise optimization should reduce or maintain token count."""
        result = self._make_result()
        assert result.token_reduction_estimate <= 1.0

    def test_to_dict_has_expected_keys(self):
        """to_dict should include all expected keys."""
        result = self._make_result()
        d = result.to_dict()
        for key in ("original", "optimized", "strategy", "changes", "token_reduction_estimate"):
            assert key in d

    def test_strategy_value_in_dict(self):
        """to_dict strategy should be the enum value string."""
        result = self._make_result()
        d = result.to_dict()
        assert d["strategy"] == "concise"

    def test_original_preserved(self):
        """OptimizationResult should preserve the original template."""
        result = self._make_result()
        assert result.original.name == "verbose"

    def test_optimized_name_includes_strategy(self):
        """Optimized template name should include the strategy."""
        result = self._make_result()
        assert "concise" in result.optimized.name

    def test_token_reduction_empty_original(self):
        """token_reduction_estimate should return 1.0 for empty template."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="empty", template_str="")
        result = optimizer.optimize(t, OptimizationStrategy.CONCISE)
        assert result.token_reduction_estimate == 1.0


@pytest.mark.unit
class TestBulkOptimization:
    """Tests for bulk_optimize across multiple templates."""

    def test_bulk_returns_list(self):
        """bulk_optimize should return a list of OptimizationResult."""
        optimizer = PromptOptimizer()
        templates = [
            PromptTemplate(name="a", template_str="Do {x}"),
            PromptTemplate(name="b", template_str="Make {y}"),
            PromptTemplate(name="c", template_str="Build {z}"),
        ]
        results = optimizer.bulk_optimize(templates, OptimizationStrategy.DETAILED)
        assert len(results) == 3
        assert all(isinstance(r, OptimizationResult) for r in results)

    def test_bulk_empty_list(self):
        """bulk_optimize with empty list should return empty list."""
        optimizer = PromptOptimizer()
        results = optimizer.bulk_optimize([], OptimizationStrategy.CONCISE)
        assert results == []

    def test_bulk_applies_same_strategy(self):
        """All results should use the same strategy."""
        optimizer = PromptOptimizer()
        templates = [
            PromptTemplate(name="a", template_str="Do {x}"),
            PromptTemplate(name="b", template_str="Make {y}"),
        ]
        results = optimizer.bulk_optimize(templates, OptimizationStrategy.CHAIN_OF_THOUGHT)
        for r in results:
            assert r.strategy == OptimizationStrategy.CHAIN_OF_THOUGHT

    def test_bulk_preserves_variables(self):
        """Optimized templates should preserve original variables."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Explain {topic} about {subject}")
        results = optimizer.bulk_optimize([t], OptimizationStrategy.DETAILED)
        assert "topic" in results[0].optimized.variables
        assert "subject" in results[0].optimized.variables

    def test_bulk_changes_non_empty(self):
        """Each result in bulk should have non-empty changes list."""
        optimizer = PromptOptimizer()
        templates = [
            PromptTemplate(name="a", template_str="Please do {x}"),
        ]
        results = optimizer.bulk_optimize(templates, OptimizationStrategy.CONCISE)
        assert len(results[0].changes) > 0


@pytest.mark.unit
class TestAvailableStrategies:
    """Tests for available_strategies listing."""

    def test_returns_list_of_strings(self):
        """available_strategies should return a list of strings."""
        optimizer = PromptOptimizer()
        strategies = optimizer.available_strategies()
        assert isinstance(strategies, list)
        assert all(isinstance(s, str) for s in strategies)

    def test_includes_all_four_strategies(self):
        """Available strategies should include all four defined strategies."""
        optimizer = PromptOptimizer()
        strategies = optimizer.available_strategies()
        assert "concise" in strategies
        assert "detailed" in strategies
        assert "chain_of_thought" in strategies
        assert "few_shot" in strategies

    def test_strategies_are_sorted(self):
        """available_strategies should return sorted list."""
        optimizer = PromptOptimizer()
        strategies = optimizer.available_strategies()
        assert strategies == sorted(strategies)

    def test_strategy_enum_values_match(self):
        """Strategy enum values should match available_strategies output."""
        optimizer = PromptOptimizer()
        strategies = optimizer.available_strategies()
        enum_values = sorted(s.value for s in OptimizationStrategy)
        assert strategies == enum_values

    def test_strategy_count(self):
        """There should be exactly 4 strategies."""
        optimizer = PromptOptimizer()
        assert len(optimizer.available_strategies()) == 4


@pytest.mark.unit
class TestOptimizationErrorHandling:
    """Tests for error cases in optimization."""

    def test_optimized_template_has_metadata(self):
        """Optimized template should include optimization metadata."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Do {task}")
        result = optimizer.optimize(t, OptimizationStrategy.DETAILED)
        assert "optimization_strategy" in result.optimized.metadata
        assert result.optimized.metadata["optimization_strategy"] == "detailed"
        assert result.optimized.metadata["source_template"] == "t"

    def test_original_template_not_mutated(self):
        """Original template should not be mutated by optimization."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Please do {task}")
        original_str = t.template_str
        optimizer.optimize(t, OptimizationStrategy.CONCISE)
        assert t.template_str == original_str

    def test_concise_no_change_needed(self):
        """Concise optimization on clean prompt should note no changes."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="clean", template_str="Explain {topic}")
        result = optimizer.optimize(t, OptimizationStrategy.CONCISE)
        # Should have at least one change entry (even if "no changes applicable")
        assert len(result.changes) >= 1

    def test_optimized_version_matches_original(self):
        """Optimized template should inherit the original version."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="t", template_str="Do {x}", version="3.2.1")
        result = optimizer.optimize(t, OptimizationStrategy.DETAILED)
        assert result.optimized.version == "3.2.1"

    def test_set_few_shot_examples_persists(self):
        """set_few_shot_examples should persist for subsequent optimizations."""
        optimizer = PromptOptimizer()
        examples = [{"input": "a", "output": "b"}]
        optimizer.set_few_shot_examples(examples)
        t = PromptTemplate(name="t", template_str="Do {x}")
        result = optimizer.optimize(t, OptimizationStrategy.FEW_SHOT)
        assert "Example 1" in result.optimized.template_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
