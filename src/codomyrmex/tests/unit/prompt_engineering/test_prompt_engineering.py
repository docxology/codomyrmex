"""Tests for prompt_engineering module."""

import pytest

try:
    from codomyrmex.prompt_engineering import (
        EvaluationCriteria,
        EvaluationResult,
        OptimizationResult,
        OptimizationStrategy,
        PromptEvaluator,
        PromptOptimizer,
        PromptTemplate,
        TemplateRegistry,
        VersionManager,
        get_default_criteria,
        score_completeness,
        score_relevance,
        score_response_length,
        score_structure,
    )

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("prompt_engineering module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# PromptTemplate
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPromptTemplate:
    """Test suite for PromptTemplate."""
    def test_create_template(self):
        """Test functionality: create template."""
        t = PromptTemplate(name="greet", template_str="Hello, {name}!")
        assert t.name == "greet"
        assert t.variables == ["name"]

    def test_auto_detect_variables(self):
        """Test functionality: auto detect variables."""
        t = PromptTemplate(name="t", template_str="{a} and {b} and {a}")
        assert sorted(t.variables) == ["a", "b"]

    def test_render(self):
        """Test functionality: render."""
        t = PromptTemplate(name="t", template_str="Say {word} to {person}")
        rendered = t.render(word="hello", person="Alice")
        assert rendered == "Say hello to Alice"

    def test_render_missing_variable_raises(self):
        """Test functionality: render missing variable raises."""
        t = PromptTemplate(name="t", template_str="Hello {name}")
        with pytest.raises(KeyError, match="Missing required"):
            t.render()

    def test_validate_returns_missing(self):
        """Test functionality: validate returns missing."""
        t = PromptTemplate(name="t", template_str="{a} {b}")
        missing = t.validate(a="ok")
        assert missing == ["b"]

    def test_validate_all_present(self):
        """Test functionality: validate all present."""
        t = PromptTemplate(name="t", template_str="{x}")
        missing = t.validate(x="present")
        assert missing == []

    def test_to_dict_and_from_dict(self):
        """Test functionality: to dict and from dict."""
        t = PromptTemplate(
            name="test",
            template_str="Do {action}",
            version="2.0.0",
            metadata={"author": "tester"},
        )
        d = t.to_dict()
        restored = PromptTemplate.from_dict(d)
        assert restored.name == "test"
        assert restored.version == "2.0.0"
        assert restored.metadata["author"] == "tester"
        assert "action" in restored.variables

    def test_explicit_variables(self):
        """Test functionality: explicit variables."""
        t = PromptTemplate(
            name="t",
            template_str="{x} {y}",
            variables=["x", "y", "z"],
        )
        assert "z" in t.variables


# ---------------------------------------------------------------------------
# TemplateRegistry
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTemplateRegistry:
    """Test suite for TemplateRegistry."""
    def _make_template(self, name="t1"):
        return PromptTemplate(name=name, template_str=f"Template {name}: {{var}}")

    def test_add_and_get(self):
        """Test functionality: add and get."""
        reg = TemplateRegistry()
        t = self._make_template("greet")
        reg.add(t)
        assert reg.get("greet") is t

    def test_add_duplicate_raises(self):
        """Test functionality: add duplicate raises."""
        reg = TemplateRegistry()
        reg.add(self._make_template("dup"))
        with pytest.raises(ValueError, match="already exists"):
            reg.add(self._make_template("dup"))

    def test_update_replaces(self):
        """Test functionality: update replaces."""
        reg = TemplateRegistry()
        reg.add(self._make_template("t"))
        new_t = PromptTemplate(name="t", template_str="Updated: {var}")
        reg.update(new_t)
        assert "Updated" in reg.get("t").template_str

    def test_remove(self):
        """Test functionality: remove."""
        reg = TemplateRegistry()
        reg.add(self._make_template("rm"))
        removed = reg.remove("rm")
        assert removed.name == "rm"
        with pytest.raises(KeyError):
            reg.get("rm")

    def test_remove_nonexistent_raises(self):
        """Test functionality: remove nonexistent raises."""
        reg = TemplateRegistry()
        with pytest.raises(KeyError):
            reg.remove("missing")

    def test_list_and_size(self):
        """Test functionality: list and size."""
        reg = TemplateRegistry()
        reg.add(self._make_template("b"))
        reg.add(self._make_template("a"))
        assert reg.list() == ["a", "b"]
        assert reg.size == 2

    def test_render_via_registry(self):
        """Test functionality: render via registry."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="greet", template_str="Hi {name}"))
        result = reg.render("greet", name="World")
        assert result == "Hi World"

    def test_search_by_name(self):
        """Test functionality: search by name."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="code_review", template_str="Review {code}"))
        reg.add(PromptTemplate(name="code_fix", template_str="Fix {code}"))
        reg.add(PromptTemplate(name="summarize", template_str="Sum {text}"))
        results = reg.search("code")
        assert len(results) == 2

    def test_export_import(self):
        """Test functionality: export import."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="a", template_str="A: {x}"))
        reg.add(PromptTemplate(name="b", template_str="B: {y}"))
        exported = reg.export_all()
        assert len(exported) == 2

        new_reg = TemplateRegistry()
        count = new_reg.import_all(exported)
        assert count == 2
        assert new_reg.size == 2


# ---------------------------------------------------------------------------
# VersionManager
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestVersionManager:
    """Test suite for VersionManager."""
    def test_create_first_version(self):
        """Test functionality: create first version."""
        vm = VersionManager()
        t = PromptTemplate(name="qa", template_str="Q: {question}")
        v = vm.create_version(t, changelog="Initial")
        assert v.version == "1.0.0"
        assert v.changelog == "Initial"

    def test_auto_increment_patch(self):
        """Test functionality: auto increment patch."""
        vm = VersionManager()
        t = PromptTemplate(name="qa", template_str="V1: {q}")
        vm.create_version(t)
        t2 = PromptTemplate(name="qa", template_str="V2: {q}")
        v2 = vm.create_version(t2)
        assert v2.version == "1.0.1"

    def test_bump_minor(self):
        """Test functionality: bump minor."""
        vm = VersionManager()
        t = PromptTemplate(name="qa", template_str="V1: {q}")
        vm.create_version(t)
        t2 = PromptTemplate(name="qa", template_str="V2: {q}")
        v2 = vm.create_version(t2, bump="minor")
        assert v2.version == "1.1.0"

    def test_get_version_latest(self):
        """Test functionality: get version latest."""
        vm = VersionManager()
        t = PromptTemplate(name="qa", template_str="V1: {q}")
        vm.create_version(t)
        t2 = PromptTemplate(name="qa", template_str="V2: {q}")
        vm.create_version(t2)
        latest = vm.get_version("qa")
        assert latest.version == "1.0.1"

    def test_get_specific_version(self):
        """Test functionality: get specific version."""
        vm = VersionManager()
        t = PromptTemplate(name="qa", template_str="V1: {q}")
        vm.create_version(t)
        t2 = PromptTemplate(name="qa", template_str="V2: {q}")
        vm.create_version(t2)
        v1 = vm.get_version("qa", "1.0.0")
        assert "V1" in v1.template.template_str

    def test_get_version_not_found(self):
        """Test functionality: get version not found."""
        vm = VersionManager()
        with pytest.raises(KeyError):
            vm.get_version("nonexistent")

    def test_list_versions(self):
        """Test functionality: list versions."""
        vm = VersionManager()
        t = PromptTemplate(name="qa", template_str="V1")
        vm.create_version(t)
        t2 = PromptTemplate(name="qa", template_str="V2")
        vm.create_version(t2)
        versions = vm.list_versions("qa")
        assert len(versions) == 2

    def test_diff(self):
        """Test functionality: diff."""
        vm = VersionManager()
        t1 = PromptTemplate(name="qa", template_str="Original text")
        vm.create_version(t1)
        t2 = PromptTemplate(name="qa", template_str="Modified text")
        vm.create_version(t2)
        diff_output = vm.diff("qa", "1.0.0", "1.0.1")
        assert "Original" in diff_output or "Modified" in diff_output

    def test_rollback(self):
        """Test functionality: rollback."""
        vm = VersionManager()
        t1 = PromptTemplate(name="qa", template_str="Original: {q}")
        vm.create_version(t1)
        t2 = PromptTemplate(name="qa", template_str="Changed: {q}")
        vm.create_version(t2)
        rolled = vm.rollback("qa", "1.0.0")
        assert "Original" in rolled.template.template_str
        assert vm.version_count("qa") == 3

    def test_version_count(self):
        """Test functionality: version count."""
        vm = VersionManager()
        assert vm.version_count("missing") == 0
        t = PromptTemplate(name="qa", template_str="V1")
        vm.create_version(t)
        assert vm.version_count("qa") == 1

    def test_export_history(self):
        """Test functionality: export history."""
        vm = VersionManager()
        t = PromptTemplate(name="qa", template_str="V1")
        vm.create_version(t)
        history = vm.export_history("qa")
        assert len(history) == 1
        assert "version" in history[0]
        assert "template" in history[0]


# ---------------------------------------------------------------------------
# PromptOptimizer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPromptOptimizer:
    """Test suite for PromptOptimizer."""
    def test_concise_optimization(self):
        """Test functionality: concise optimization."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(
            name="verbose",
            template_str="I would like you to please explain {topic} in detail",
        )
        result = optimizer.optimize(t, OptimizationStrategy.CONCISE)
        assert isinstance(result, OptimizationResult)
        assert result.strategy == OptimizationStrategy.CONCISE
        assert len(result.changes) > 0

    def test_detailed_optimization(self):
        """Test functionality: detailed optimization."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="simple", template_str="Explain {topic}")
        result = optimizer.optimize(t, OptimizationStrategy.DETAILED)
        assert "Task" in result.optimized.template_str

    def test_chain_of_thought_optimization(self):
        """Test functionality: chain of thought optimization."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(name="solve", template_str="Solve {problem}")
        result = optimizer.optimize(t, OptimizationStrategy.CHAIN_OF_THOUGHT)
        assert "step" in result.optimized.template_str.lower()

    def test_few_shot_optimization(self):
        """Test functionality: few shot optimization."""
        optimizer = PromptOptimizer()
        optimizer.set_few_shot_examples([
            {"input": "2+2", "output": "4"},
            {"input": "3*3", "output": "9"},
        ])
        t = PromptTemplate(name="math", template_str="Calculate {expression}")
        result = optimizer.optimize(t, OptimizationStrategy.FEW_SHOT)
        assert "Example" in result.optimized.template_str

    def test_token_reduction_estimate(self):
        """Test functionality: token reduction estimate."""
        optimizer = PromptOptimizer()
        t = PromptTemplate(
            name="verbose",
            template_str="I would like you to please kindly explain {topic} in great detail",
        )
        result = optimizer.optimize(t, OptimizationStrategy.CONCISE)
        assert result.token_reduction_estimate <= 1.0

    def test_bulk_optimize(self):
        """Test functionality: bulk optimize."""
        optimizer = PromptOptimizer()
        templates = [
            PromptTemplate(name="a", template_str="Do {x}"),
            PromptTemplate(name="b", template_str="Make {y}"),
        ]
        results = optimizer.bulk_optimize(templates, OptimizationStrategy.DETAILED)
        assert len(results) == 2

    def test_available_strategies(self):
        """Test functionality: available strategies."""
        optimizer = PromptOptimizer()
        strategies = optimizer.available_strategies()
        assert "concise" in strategies
        assert "detailed" in strategies
        assert "chain_of_thought" in strategies
        assert "few_shot" in strategies


# ---------------------------------------------------------------------------
# Evaluation scorer functions
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScorerFunctions:
    """Test suite for ScorerFunctions."""
    def test_score_response_length_short(self):
        """Test functionality: score response length short."""
        score = score_response_length("prompt", "short")
        assert 0.0 <= score <= 1.0

    def test_score_response_length_ideal(self):
        """Test functionality: score response length ideal."""
        response = " ".join(["word"] * 100)
        score = score_response_length("prompt", response)
        assert score == 1.0

    def test_score_relevance_with_overlap(self):
        """Test functionality: score relevance with overlap."""
        prompt = "Explain machine learning algorithms"
        response = "Machine learning algorithms include decision trees and neural networks."
        score = score_relevance(prompt, response)
        assert score > 0.0

    def test_score_relevance_no_overlap(self):
        """Test functionality: score relevance no overlap."""
        score = score_relevance("quantum physics", "cats and dogs")
        assert score == 0.0

    def test_score_structure_with_formatting(self):
        """Test functionality: score structure with formatting."""
        response = "# Title\n\n- Point one\n- Point two\n\nConclusion."
        score = score_structure("prompt", response)
        assert score > 0.5

    def test_score_completeness_with_question(self):
        """Test functionality: score completeness with question."""
        score = score_completeness(
            "What is Python?",
            "Python is a high-level programming language known for readability and versatility."
        )
        assert score > 0.5


# ---------------------------------------------------------------------------
# PromptEvaluator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPromptEvaluator:
    """Test suite for PromptEvaluator."""
    def test_evaluate_returns_result(self):
        """Test functionality: evaluate returns result."""
        evaluator = PromptEvaluator()
        result = evaluator.evaluate(
            prompt="Explain testing",
            response="Testing is the process of verifying software correctness. "
                     "It includes unit tests, integration tests, and end-to-end tests.",
        )
        assert isinstance(result, EvaluationResult)
        assert 0.0 <= result.weighted_score <= 1.0
        assert len(result.scores) > 0

    def test_evaluate_with_default_criteria(self):
        """Test functionality: evaluate with default criteria."""
        criteria = get_default_criteria()
        assert len(criteria) == 4
        names = [c.name for c in criteria]
        assert "relevance" in names
        assert "completeness" in names

    def test_evaluate_batch(self):
        """Test functionality: evaluate batch."""
        evaluator = PromptEvaluator()
        pairs = [
            ("What is AI?", "AI is artificial intelligence."),
            ("What is ML?", "ML is machine learning."),
        ]
        results = evaluator.evaluate_batch(pairs)
        assert len(results) == 2

    def test_compare_responses(self):
        """Test functionality: compare responses."""
        evaluator = PromptEvaluator()
        comparison = evaluator.compare_responses(
            prompt="What is Python?",
            responses=[
                "A snake.",
                "Python is a high-level programming language.\n\n"
                "- Readable syntax\n- Large ecosystem\n- Versatile applications.",
            ],
        )
        assert "ranking" in comparison
        assert "best_index" in comparison
        assert "statistics" in comparison

    def test_add_and_remove_criteria(self):
        """Test functionality: add and remove criteria."""
        evaluator = PromptEvaluator(criteria=[])
        custom = EvaluationCriteria(
            name="custom",
            weight=1.0,
            scorer_fn=lambda p, r: 0.8,
            description="Always returns 0.8",
        )
        evaluator.add_criteria(custom)
        assert "custom" in evaluator.criteria_names()
        evaluator.remove_criteria("custom")
        assert "custom" not in evaluator.criteria_names()

    def test_evaluation_result_to_dict(self):
        """Test functionality: evaluation result to dict."""
        evaluator = PromptEvaluator()
        result = evaluator.evaluate("test prompt", "test response")
        d = result.to_dict()
        assert "weighted_score" in d
        assert "scores" in d
