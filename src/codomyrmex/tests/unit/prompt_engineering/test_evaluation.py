"""Zero-Mock tests for prompt evaluation and scoring.

Tests for individual scorer functions (relevance, response_length,
structure, completeness), EvaluationCriteria, EvaluationResult,
PromptEvaluator with default and custom criteria, batch evaluation,
and response comparison.
"""

import pytest

try:
    from codomyrmex.prompt_engineering.evaluation import (
        EvaluationCriteria,
        EvaluationResult,
        PromptEvaluator,
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
    pytest.skip("prompt_engineering.evaluation not available", allow_module_level=True)


@pytest.mark.unit
class TestScoreResponseLength:
    """Tests for the score_response_length scorer function."""

    def test_very_short_response(self):
        """Very short response (< 10 words) should score low."""
        score = score_response_length("prompt", "short")
        assert 0.0 <= score <= 0.5

    def test_ideal_length_response(self):
        """Response with 50-500 words should score 1.0."""
        response = " ".join(["word"] * 100)
        score = score_response_length("prompt", response)
        assert score == 1.0

    def test_fifty_words_is_ideal(self):
        """Exactly 50 words should score 1.0."""
        response = " ".join(["word"] * 50)
        score = score_response_length("prompt", response)
        assert score == 1.0

    def test_very_long_response(self):
        """Very long response (> 1000 words) should score lower."""
        response = " ".join(["word"] * 1500)
        score = score_response_length("prompt", response)
        assert score == 0.5

    def test_empty_response(self):
        """Empty response should score low."""
        score = score_response_length("prompt", "")
        assert score <= 0.5

    def test_score_always_bounded(self):
        """Score should always be between 0.0 and 1.0."""
        for n in (0, 1, 5, 25, 75, 200, 500, 800, 1200):
            response = " ".join(["w"] * n)
            score = score_response_length("p", response)
            assert 0.0 <= score <= 1.0


@pytest.mark.unit
class TestScoreRelevance:
    """Tests for the score_relevance scorer function."""

    def test_high_overlap(self):
        """Response containing all prompt keywords should score high."""
        prompt = "Explain machine learning algorithms"
        response = "Machine learning algorithms include decision trees and neural networks."
        score = score_relevance(prompt, response)
        assert score > 0.5

    def test_no_overlap(self):
        """Response with no keyword overlap should score 0.0."""
        score = score_relevance("quantum physics research", "cats and dogs play")
        assert score == 0.0

    def test_partial_overlap(self):
        """Partial keyword overlap should score between 0 and 1."""
        prompt = "Explain Python programming language features"
        response = "Python is versatile."
        score = score_relevance(prompt, response)
        assert 0.0 < score < 1.0

    def test_short_prompt_words_ignored(self):
        """Words shorter than 4 characters should be ignored."""
        # "is" and "a" are < 4 chars, should not count
        prompt = "What is a test?"
        score = score_relevance(prompt, "completely unrelated text here")
        # "test" and "What" are 4+ chars; response doesn't contain them
        assert score <= 0.5

    def test_empty_prompt_returns_one(self):
        """Empty prompt should return 1.0 (no keywords to match)."""
        score = score_relevance("", "Any response text here")
        assert score == 1.0

    def test_case_insensitive(self):
        """Matching should be case-insensitive."""
        score = score_relevance("PYTHON PROGRAMMING", "python programming is great")
        assert score > 0.5


@pytest.mark.unit
class TestScoreStructure:
    """Tests for the score_structure scorer function."""

    def test_well_formatted_response(self):
        """Response with headers, bullets, and paragraphs should score high."""
        response = "# Title\n\n- Point one\n- Point two\n\nConclusion paragraph."
        score = score_structure("prompt", response)
        assert score > 0.5

    def test_single_line_response(self):
        """Single-line response should score lower on structure."""
        score = score_structure("prompt", "Just a single line.")
        assert score < 1.0

    def test_numbered_list_response(self):
        """Response with numbered list should get structure credit."""
        response = "Steps:\n\n1. First step\n2. Second step\n3. Third step"
        score = score_structure("prompt", response)
        assert score > 0.0

    def test_empty_response(self):
        """Empty response should score low on structure."""
        score = score_structure("prompt", "")
        assert score <= 0.5

    def test_multiple_paragraphs(self):
        """Response with multiple paragraphs should get paragraph credit."""
        response = "First paragraph.\n\nSecond paragraph."
        score = score_structure("prompt", response)
        assert score > 0.0

    def test_score_bounded(self):
        """Structure score should be between 0.0 and 1.0."""
        score = score_structure("prompt", "any response")
        assert 0.0 <= score <= 1.0


@pytest.mark.unit
class TestScoreCompleteness:
    """Tests for the score_completeness scorer function."""

    def test_question_with_good_answer(self):
        """Question with detailed answer should score high."""
        score = score_completeness(
            "What is Python?",
            "Python is a high-level programming language known for readability and versatility.",
        )
        assert score > 0.5

    def test_question_with_empty_answer(self):
        """Question with empty answer should score low."""
        score = score_completeness("What is Python?", "")
        assert score < 0.5

    def test_non_question_prompt(self):
        """Non-question prompt should get full marks on the question check."""
        score = score_completeness(
            "Summarize the document",
            "The document covers several topics including architecture and design.",
        )
        assert score > 0.5

    def test_truncated_response_penalized(self):
        """Response that appears truncated (no terminal punctuation) should score lower."""
        score_complete = score_completeness("prompt", "Full answer ending properly.")
        score_truncated = score_completeness("prompt", "Answer that seems to cut off mid")
        assert score_complete >= score_truncated

    def test_very_short_answer(self):
        """Very short answer (< 3 words) should score lower on meaningful content."""
        score = score_completeness("What is AI?", "AI")
        assert score < 1.0

    def test_score_bounded(self):
        """Completeness score should be between 0.0 and 1.0."""
        score = score_completeness("prompt?", "response")
        assert 0.0 <= score <= 1.0


@pytest.mark.unit
class TestEvaluationCriteria:
    """Tests for the EvaluationCriteria dataclass."""

    def test_criteria_creation(self):
        """EvaluationCriteria should initialize with name, weight, scorer."""
        criteria = EvaluationCriteria(
            name="test",
            weight=0.5,
            scorer_fn=lambda p, r: 0.7,
        )
        assert criteria.name == "test"
        assert criteria.weight == 0.5

    def test_score_method_calls_scorer(self):
        """score() should call the scorer function and return its result."""
        criteria = EvaluationCriteria(
            name="constant",
            weight=1.0,
            scorer_fn=lambda p, r: 0.85,
        )
        assert criteria.score("prompt", "response") == 0.85

    def test_score_clamps_above_one(self):
        """score() should clamp values above 1.0 to 1.0."""
        criteria = EvaluationCriteria(
            name="over",
            weight=1.0,
            scorer_fn=lambda p, r: 1.5,
        )
        assert criteria.score("p", "r") == 1.0

    def test_score_clamps_below_zero(self):
        """score() should clamp values below 0.0 to 0.0."""
        criteria = EvaluationCriteria(
            name="under",
            weight=1.0,
            scorer_fn=lambda p, r: -0.5,
        )
        assert criteria.score("p", "r") == 0.0

    def test_description_field(self):
        """Description should be stored and accessible."""
        criteria = EvaluationCriteria(
            name="test",
            weight=1.0,
            scorer_fn=lambda p, r: 0.5,
            description="A test criterion",
        )
        assert criteria.description == "A test criterion"


@pytest.mark.unit
class TestEvaluationResult:
    """Tests for EvaluationResult dataclass and serialization."""

    def test_result_creation(self):
        """EvaluationResult should store prompt, response, scores."""
        result = EvaluationResult(
            prompt="test prompt",
            response="test response",
            scores={"relevance": 0.8},
            weighted_score=0.8,
        )
        assert result.prompt == "test prompt"
        assert result.weighted_score == 0.8

    def test_to_dict_structure(self):
        """to_dict should include all expected keys."""
        result = EvaluationResult(
            prompt="p",
            response="r",
            scores={"a": 0.5},
            weighted_score=0.5,
            details={"count": 1},
        )
        d = result.to_dict()
        for key in ("prompt", "response", "scores", "weighted_score", "details"):
            assert key in d

    def test_to_dict_truncates_long_prompt(self):
        """to_dict should truncate prompts longer than 200 chars."""
        long_prompt = "x" * 300
        result = EvaluationResult(prompt=long_prompt, response="r")
        d = result.to_dict()
        assert len(d["prompt"]) < 300
        assert d["prompt"].endswith("...")

    def test_to_dict_truncates_long_response(self):
        """to_dict should truncate responses longer than 200 chars."""
        long_response = "y" * 300
        result = EvaluationResult(prompt="p", response=long_response)
        d = result.to_dict()
        assert len(d["response"]) < 300
        assert d["response"].endswith("...")

    def test_default_scores_empty(self):
        """Default scores should be an empty dict."""
        result = EvaluationResult(prompt="p", response="r")
        assert result.scores == {}
        assert result.weighted_score == 0.0


@pytest.mark.unit
class TestPromptEvaluator:
    """Tests for PromptEvaluator with default and custom criteria."""

    def test_evaluate_returns_result(self):
        """evaluate() should return an EvaluationResult."""
        evaluator = PromptEvaluator()
        result = evaluator.evaluate(
            prompt="Explain testing",
            response="Testing is the process of verifying software. "
                     "It includes unit tests, integration tests, and end-to-end tests.",
        )
        assert isinstance(result, EvaluationResult)
        assert 0.0 <= result.weighted_score <= 1.0

    def test_evaluate_with_default_criteria(self):
        """Default evaluator should use 4 criteria."""
        evaluator = PromptEvaluator()
        result = evaluator.evaluate("prompt", "response text here for evaluation")
        assert len(result.scores) == 4

    def test_criteria_names(self):
        """criteria_names() should return sorted names of active criteria."""
        evaluator = PromptEvaluator()
        names = evaluator.criteria_names()
        assert isinstance(names, list)
        assert "relevance" in names
        assert "completeness" in names
        assert names == sorted(names)

    def test_custom_criteria_only(self):
        """Evaluator with custom criteria should use only those."""
        custom = EvaluationCriteria(
            name="always_half",
            weight=1.0,
            scorer_fn=lambda p, r: 0.5,
        )
        evaluator = PromptEvaluator(criteria=[custom])
        result = evaluator.evaluate("p", "r")
        assert result.scores == {"always_half": 0.5}
        assert result.weighted_score == 0.5

    def test_add_criteria(self):
        """add_criteria should add a new criterion."""
        evaluator = PromptEvaluator(criteria=[])
        custom = EvaluationCriteria(
            name="custom",
            weight=1.0,
            scorer_fn=lambda p, r: 0.8,
        )
        evaluator.add_criteria(custom)
        assert "custom" in evaluator.criteria_names()

    def test_remove_criteria(self):
        """remove_criteria should remove by name."""
        evaluator = PromptEvaluator()
        initial_count = len(evaluator.criteria)
        assert evaluator.remove_criteria("relevance") is True
        assert len(evaluator.criteria) == initial_count - 1
        assert "relevance" not in evaluator.criteria_names()

    def test_remove_nonexistent_criteria(self):
        """remove_criteria should return False for unknown name."""
        evaluator = PromptEvaluator()
        assert evaluator.remove_criteria("nonexistent_xyz") is False


@pytest.mark.unit
class TestPromptEvaluatorBatch:
    """Tests for batch evaluation and response comparison."""

    def test_evaluate_batch(self):
        """evaluate_batch should return results for each pair."""
        evaluator = PromptEvaluator()
        pairs = [
            ("What is AI?", "AI is artificial intelligence used in many fields."),
            ("What is ML?", "ML is machine learning, a subset of AI."),
            ("What is DL?", "DL is deep learning using neural networks."),
        ]
        results = evaluator.evaluate_batch(pairs)
        assert len(results) == 3
        assert all(isinstance(r, EvaluationResult) for r in results)

    def test_evaluate_batch_empty(self):
        """evaluate_batch with empty list should return empty list."""
        evaluator = PromptEvaluator()
        results = evaluator.evaluate_batch([])
        assert results == []

    def test_compare_responses(self):
        """compare_responses should rank responses and provide stats."""
        evaluator = PromptEvaluator()
        comparison = evaluator.compare_responses(
            prompt="What is Python?",
            responses=[
                "A snake.",
                "Python is a high-level programming language.\n\n"
                "- Readable syntax\n- Large ecosystem\n- Versatile.",
            ],
        )
        assert "ranking" in comparison
        assert "best_index" in comparison
        assert "statistics" in comparison
        assert comparison["best_index"] is not None

    def test_compare_responses_statistics(self):
        """compare_responses statistics should have expected keys."""
        evaluator = PromptEvaluator()
        comparison = evaluator.compare_responses(
            prompt="Explain AI",
            responses=[
                "AI is artificial intelligence.",
                "AI stands for artificial intelligence and it transforms industries.",
            ],
        )
        stats = comparison["statistics"]
        for key in ("mean", "stdev", "min", "max"):
            assert key in stats
            assert isinstance(stats[key], float)

    def test_compare_single_response(self):
        """compare_responses with single response should work."""
        evaluator = PromptEvaluator()
        comparison = evaluator.compare_responses(
            prompt="Explain",
            responses=["Single detailed response about the topic at hand."],
        )
        assert comparison["best_index"] == 0
        assert comparison["statistics"]["stdev"] == 0.0


@pytest.mark.unit
class TestDefaultCriteria:
    """Tests for the get_default_criteria function."""

    def test_returns_list(self):
        """get_default_criteria should return a list."""
        criteria = get_default_criteria()
        assert isinstance(criteria, list)

    def test_four_default_criteria(self):
        """There should be exactly 4 default criteria."""
        criteria = get_default_criteria()
        assert len(criteria) == 4

    def test_criteria_names(self):
        """Default criteria should include relevance, completeness, structure, length."""
        criteria = get_default_criteria()
        names = {c.name for c in criteria}
        assert names == {"relevance", "completeness", "structure", "length"}

    def test_weights_sum_to_one(self):
        """Default criteria weights should sum to 1.0."""
        criteria = get_default_criteria()
        total = sum(c.weight for c in criteria)
        assert abs(total - 1.0) < 0.01

    def test_all_criteria_are_evaluationcriteria(self):
        """All items should be EvaluationCriteria instances."""
        criteria = get_default_criteria()
        for c in criteria:
            assert isinstance(c, EvaluationCriteria)

    def test_all_criteria_have_descriptions(self):
        """All default criteria should have non-empty descriptions."""
        criteria = get_default_criteria()
        for c in criteria:
            assert len(c.description) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
