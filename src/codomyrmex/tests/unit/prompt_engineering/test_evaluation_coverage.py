"""Zero-mock tests for prompt_engineering.evaluation module.

Targets uncovered paths in scorer functions, PromptEvaluator, and comparison logic.
All tests use real function calls with inline data.
"""

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


class TestScoreResponseLength:
    """Tests for score_response_length scorer."""

    def test_very_short_response_scores_low(self):
        score = score_response_length("prompt", "hi")
        assert score == 0.2

    def test_medium_short_response(self):
        # 20 words: between 10-50, interpolated
        response = " ".join(["word"] * 20)
        score = score_response_length("prompt", response)
        assert 0.5 < score < 1.0

    def test_ideal_length_response(self):
        # 200 words is in 50-500 range
        response = " ".join(["word"] * 200)
        score = score_response_length("prompt", response)
        assert score == 1.0

    def test_long_response_scores_lower(self):
        # 750 words: between 500-1000 range
        response = " ".join(["word"] * 750)
        score = score_response_length("prompt", response)
        assert 0.5 < score < 1.0

    def test_very_long_response_scores_half(self):
        # 1500 words: >1000
        response = " ".join(["word"] * 1500)
        score = score_response_length("prompt", response)
        assert score == 0.5

    def test_exactly_50_words_scores_1(self):
        response = " ".join(["word"] * 50)
        score = score_response_length("prompt", response)
        assert score == 1.0

    def test_exactly_500_words_scores_1(self):
        response = " ".join(["word"] * 500)
        score = score_response_length("prompt", response)
        assert score == 1.0


class TestScoreRelevance:
    """Tests for score_relevance scorer."""

    def test_empty_prompt_keywords_returns_1(self):
        # prompt with only short words (< 4 chars)
        score = score_relevance("go do it", "anything here")
        assert score == 1.0

    def test_perfect_keyword_overlap(self):
        prompt = "explain neural networks"
        response = "Neural networks are a type of machine learning model"
        score = score_relevance(prompt, response)
        assert score > 0.5

    def test_zero_keyword_overlap(self):
        prompt = "explain quantum computing"
        response = "Hello world this is a test"
        score = score_relevance(prompt, response)
        assert score < 0.5

    def test_partial_keyword_overlap(self):
        prompt = "explain python programming language"
        response = "Python is great but not a programming topic"
        score = score_relevance(prompt, response)
        assert 0.0 < score < 1.0

    def test_case_insensitive_matching(self):
        prompt = "Explain PYTHON"
        response = "python is a language"
        score = score_relevance(prompt, response)
        assert score > 0.0


class TestScoreStructure:
    """Tests for score_structure scorer."""

    def test_plain_text_no_structure(self):
        response = "This is a plain sentence without any structure."
        score = score_structure("prompt", response)
        # Only multiline check (has line breaks? No) but it's one line
        assert 0.0 <= score <= 1.0

    def test_response_with_bullet_points(self):
        response = "Here are items:\n- Item one\n- Item two\n- Item three"
        score = score_structure("prompt", response)
        assert score > 0.25

    def test_response_with_numbered_list(self):
        response = "Steps:\n1. First step\n2. Second step\n3. Third step"
        score = score_structure("prompt", response)
        assert score > 0.25

    def test_response_with_headers(self):
        response = "## Overview\nThis is content.\n\n## Details\nMore content."
        score = score_structure("prompt", response)
        assert score > 0.5

    def test_structured_response_scores_highest(self):
        response = (
            "## Title\n\nParagraph one.\n\nParagraph two.\n\n"
            "- Bullet 1\n- Bullet 2\n\n**Bold text here**"
        )
        score = score_structure("prompt", response)
        assert score >= 0.75

    def test_score_clamped_between_0_and_1(self):
        score = score_structure("prompt", "any response")
        assert 0.0 <= score <= 1.0


class TestScoreCompleteness:
    """Tests for score_completeness scorer."""

    def test_question_with_substantial_answer(self):
        prompt = "What is the capital of France?"
        response = (
            "The capital of France is Paris, which is located in northern France."
        )
        score = score_completeness(prompt, response)
        assert score > 0.5

    def test_question_with_empty_answer_scores_low(self):
        prompt = "What is Python?"
        response = "Yes"
        score = score_completeness(prompt, response)
        assert score < 0.8

    def test_non_question_always_gets_full_intent_score(self):
        prompt = "Write a poem about autumn"
        response = "Leaves fall and float on gentle winds of change."
        score = score_completeness(prompt, response)
        assert score > 0.5

    def test_response_ending_with_punctuation_scores_higher(self):
        prompt = "Describe something."
        response = "This is a complete response with proper ending."
        score = score_completeness(prompt, response)
        assert score > 0.5

    def test_truncated_response_scores_lower(self):
        prompt = "What is machine learning"
        response = "Machine learning is a field that"
        score = score_completeness(prompt, response)
        assert score < 1.0

    def test_short_word_count_penalized(self):
        prompt = "Explain everything?"
        response = "Yes it"
        score = score_completeness(prompt, response)
        assert score < 0.8


class TestEvaluationCriteria:
    """Tests for EvaluationCriteria dataclass."""

    def test_construction(self):
        criterion = EvaluationCriteria(
            name="test_criterion",
            weight=0.5,
            scorer_fn=lambda p, r: 0.8,
            description="Test criterion",
        )
        assert criterion.name == "test_criterion"
        assert criterion.weight == 0.5
        assert criterion.description == "Test criterion"

    def test_score_clamps_above_1(self):
        criterion = EvaluationCriteria(
            name="over", weight=1.0, scorer_fn=lambda p, r: 2.0
        )
        score = criterion.score("prompt", "response")
        assert score == 1.0

    def test_score_clamps_below_0(self):
        criterion = EvaluationCriteria(
            name="under", weight=1.0, scorer_fn=lambda p, r: -1.0
        )
        score = criterion.score("prompt", "response")
        assert score == 0.0

    def test_score_passes_normal_value_through(self):
        criterion = EvaluationCriteria(
            name="normal", weight=0.5, scorer_fn=lambda p, r: 0.75
        )
        score = criterion.score("prompt", "response")
        assert score == 0.75


class TestEvaluationResult:
    """Tests for EvaluationResult.to_dict method."""

    def test_to_dict_short_prompt(self):
        result = EvaluationResult(
            prompt="short prompt",
            response="short response",
            scores={"relevance": 0.8},
            weighted_score=0.8,
        )
        d = result.to_dict()
        assert d["prompt"] == "short prompt"
        assert d["response"] == "short response"
        assert d["weighted_score"] == 0.8

    def test_to_dict_long_prompt_truncated(self):
        long_prompt = "x" * 300
        result = EvaluationResult(
            prompt=long_prompt,
            response="resp",
            scores={},
            weighted_score=0.0,
        )
        d = result.to_dict()
        assert d["prompt"].endswith("...")
        assert len(d["prompt"]) < 210

    def test_to_dict_long_response_truncated(self):
        result = EvaluationResult(
            prompt="p",
            response="y" * 300,
            scores={},
            weighted_score=0.0,
        )
        d = result.to_dict()
        assert d["response"].endswith("...")


class TestGetDefaultCriteria:
    """Tests for get_default_criteria function."""

    def test_returns_list(self):
        criteria = get_default_criteria()
        assert isinstance(criteria, list)

    def test_contains_expected_criteria(self):
        criteria = get_default_criteria()
        names = {c.name for c in criteria}
        assert "relevance" in names
        assert "completeness" in names
        assert "structure" in names
        assert "length" in names

    def test_weights_sum_to_1(self):
        criteria = get_default_criteria()
        total_weight = sum(c.weight for c in criteria)
        assert abs(total_weight - 1.0) < 0.001


class TestPromptEvaluator:
    """Tests for PromptEvaluator class."""

    def test_init_with_default_criteria(self):
        evaluator = PromptEvaluator()
        assert len(evaluator.criteria) == 4

    def test_init_with_custom_criteria(self):
        custom = [
            EvaluationCriteria(name="custom", weight=1.0, scorer_fn=lambda p, r: 0.5)
        ]
        evaluator = PromptEvaluator(criteria=custom)
        assert len(evaluator.criteria) == 1
        assert evaluator.criteria[0].name == "custom"

    def test_add_criteria(self):
        evaluator = PromptEvaluator(criteria=[])
        criterion = EvaluationCriteria(
            name="added", weight=0.5, scorer_fn=lambda p, r: 0.9
        )
        evaluator.add_criteria(criterion)
        assert len(evaluator.criteria) == 1

    def test_remove_criteria_success(self):
        criteria = get_default_criteria()
        evaluator = PromptEvaluator(criteria=criteria)
        removed = evaluator.remove_criteria("relevance")
        assert removed is True
        names = [c.name for c in evaluator.criteria]
        assert "relevance" not in names

    def test_remove_criteria_not_found(self):
        evaluator = PromptEvaluator()
        removed = evaluator.remove_criteria("nonexistent_criterion")
        assert removed is False

    def test_evaluate_returns_result(self):
        evaluator = PromptEvaluator()
        result = evaluator.evaluate(
            "What is Python?", "Python is a programming language."
        )
        assert result.prompt == "What is Python?"
        assert result.response == "Python is a programming language."
        assert 0.0 <= result.weighted_score <= 1.0
        assert len(result.scores) == 4

    def test_evaluate_with_override_criteria(self):
        evaluator = PromptEvaluator()
        custom = [
            EvaluationCriteria(name="custom", weight=1.0, scorer_fn=lambda p, r: 0.42)
        ]
        result = evaluator.evaluate("prompt", "response", criteria=custom)
        assert result.scores.get("custom") == 0.42
        assert len(result.scores) == 1

    def test_evaluate_weighted_score_calculation(self):
        fixed_scorer = lambda p, r: 1.0
        criteria = [
            EvaluationCriteria(name="a", weight=0.6, scorer_fn=fixed_scorer),
            EvaluationCriteria(name="b", weight=0.4, scorer_fn=fixed_scorer),
        ]
        evaluator = PromptEvaluator(criteria=criteria)
        result = evaluator.evaluate("p", "r")
        assert abs(result.weighted_score - 1.0) < 0.001

    def test_evaluate_empty_criteria(self):
        evaluator = PromptEvaluator(criteria=[])
        result = evaluator.evaluate("prompt", "response")
        assert result.weighted_score == 0.0
        assert result.scores == {}

    def test_evaluate_batch(self):
        evaluator = PromptEvaluator()
        pairs = [
            ("What is 2+2?", "The answer is 4."),
            ("Explain Python", "Python is a programming language"),
        ]
        results = evaluator.evaluate_batch(pairs)
        assert len(results) == 2
        for r in results:
            assert 0.0 <= r.weighted_score <= 1.0

    def test_compare_responses_returns_ranking(self):
        evaluator = PromptEvaluator()
        prompt = "What is Python?"
        responses = [
            "Python is a language",
            "Python is a high-level, interpreted programming language known for its simplicity.",
        ]
        comparison = evaluator.compare_responses(prompt, responses)
        assert "results" in comparison
        assert "ranking" in comparison
        assert "best_index" in comparison
        assert "statistics" in comparison
        assert len(comparison["results"]) == 2
        assert len(comparison["ranking"]) == 2

    def test_compare_responses_statistics(self):
        evaluator = PromptEvaluator()
        comparison = evaluator.compare_responses(
            "prompt",
            ["response one that is detailed", "shorter response"],
        )
        stats = comparison["statistics"]
        assert "mean" in stats
        assert "stdev" in stats
        assert "min" in stats
        assert "max" in stats
        assert stats["min"] <= stats["max"]

    def test_criteria_names_sorted(self):
        evaluator = PromptEvaluator()
        names = evaluator.criteria_names()
        assert names == sorted(names)
        assert "relevance" in names
        assert "completeness" in names
