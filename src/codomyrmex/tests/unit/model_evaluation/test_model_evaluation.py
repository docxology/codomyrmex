"""Tests for model_evaluation module."""

import re

import pytest

try:
    from codomyrmex.model_ops.evaluation import (
        BenchmarkCase,
        BenchmarkResult,
        BenchmarkSuite,
        CompositeScorer,
        ContainsScorer,
        ExactMatchScorer,
        LengthScorer,
        QualityAnalyzer,
        QualityDimension,
        QualityReport,
        RegexScorer,
        Scorer,
        SuiteResult,
        WeightedScorer,
        analyze_quality,
        create_default_scorer,
    )

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("model_evaluation module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# ExactMatchScorer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExactMatchScorer:
    """Test suite for ExactMatchScorer."""
    def test_exact_match(self):
        """Test functionality: exact match."""
        scorer = ExactMatchScorer()
        assert scorer.score("hello", "hello") == 1.0

    def test_no_match(self):
        """Test functionality: no match."""
        scorer = ExactMatchScorer()
        assert scorer.score("hello", "world") == 0.0

    def test_case_insensitive(self):
        """Test functionality: case insensitive."""
        scorer = ExactMatchScorer(case_sensitive=False)
        assert scorer.score("Hello", "hello") == 1.0

    def test_strip_whitespace(self):
        """Test functionality: strip whitespace."""
        scorer = ExactMatchScorer(strip_whitespace=True)
        assert scorer.score("  hello  ", "hello") == 1.0

    def test_name_property(self):
        """Test functionality: name property."""
        assert ExactMatchScorer().name == "exact_match"

    def test_score_batch(self):
        """Test functionality: score batch."""
        scorer = ExactMatchScorer(case_sensitive=False)
        pairs = [("hello", "hello"), ("world", "WORLD"), ("a", "b")]
        results = scorer.score_batch(pairs)
        assert results == [1.0, 1.0, 0.0]


# ---------------------------------------------------------------------------
# ContainsScorer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContainsScorer:
    """Test suite for ContainsScorer."""
    def test_contains_match(self):
        """Test functionality: contains match."""
        scorer = ContainsScorer()
        assert scorer.score("The answer is 42", "42") == 1.0

    def test_contains_no_match(self):
        """Test functionality: contains no match."""
        scorer = ContainsScorer()
        assert scorer.score("The answer is 42", "99") == 0.0

    def test_case_insensitive_default(self):
        """Test functionality: case insensitive default."""
        scorer = ContainsScorer()
        assert scorer.score("Hello World", "hello") == 1.0

    def test_case_sensitive(self):
        """Test functionality: case sensitive."""
        scorer = ContainsScorer(case_sensitive=True)
        assert scorer.score("Hello World", "hello") == 0.0


# ---------------------------------------------------------------------------
# LengthScorer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLengthScorer:
    """Test suite for LengthScorer."""
    def test_within_range(self):
        """Test functionality: within range."""
        scorer = LengthScorer(min_length=5, max_length=50)
        assert scorer.score("Hello World", "") == 1.0

    def test_below_range(self):
        """Test functionality: below range."""
        scorer = LengthScorer(min_length=10, max_length=50)
        score = scorer.score("Hi", "")
        assert 0.0 <= score < 1.0

    def test_above_range(self):
        """Test functionality: above range."""
        scorer = LengthScorer(min_length=1, max_length=5)
        score = scorer.score("This is way too long", "")
        assert 0.0 <= score < 1.0

    def test_invalid_min_length(self):
        """Test functionality: invalid min length."""
        with pytest.raises(ValueError):
            LengthScorer(min_length=-1)

    def test_invalid_max_less_than_min(self):
        """Test functionality: invalid max less than min."""
        with pytest.raises(ValueError):
            LengthScorer(min_length=10, max_length=5)


# ---------------------------------------------------------------------------
# RegexScorer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRegexScorer:
    """Test suite for RegexScorer."""
    def test_regex_search(self):
        """Test functionality: regex search."""
        scorer = RegexScorer()
        assert scorer.score("The value is 42.", r"\d+") == 1.0

    def test_regex_no_match(self):
        """Test functionality: regex no match."""
        scorer = RegexScorer()
        assert scorer.score("no numbers here", r"\d+") == 0.0

    def test_regex_full_match(self):
        """Test functionality: regex full match."""
        scorer = RegexScorer(full_match=True)
        assert scorer.score("42", r"\d+") == 1.0
        assert scorer.score("value 42", r"\d+") == 0.0

    def test_invalid_regex_returns_zero(self):
        """Test functionality: invalid regex returns zero."""
        scorer = RegexScorer()
        assert scorer.score("test", "[invalid") == 0.0


# ---------------------------------------------------------------------------
# CompositeScorer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCompositeScorer:
    """Test suite for CompositeScorer."""
    def test_empty_returns_zero(self):
        """Test functionality: empty returns zero."""
        scorer = CompositeScorer()
        assert scorer.score("a", "b") == 0.0

    def test_single_scorer(self):
        """Test functionality: single scorer."""
        scorer = CompositeScorer()
        scorer.add_scorer(ExactMatchScorer(case_sensitive=False), weight=1.0)
        assert scorer.score("hello", "HELLO") == 1.0

    def test_weighted_average(self):
        """Test functionality: weighted average."""
        scorer = CompositeScorer([
            WeightedScorer(ExactMatchScorer(), weight=1.0),
            WeightedScorer(ContainsScorer(), weight=1.0),
        ])
        # Exact match fails (case sensitive), contains succeeds
        score = scorer.score("Hello", "hello")
        assert score == 0.5

    def test_add_scorer_negative_weight(self):
        """Test functionality: add scorer negative weight."""
        scorer = CompositeScorer()
        with pytest.raises(ValueError, match="positive"):
            scorer.add_scorer(ExactMatchScorer(), weight=-1.0)

    def test_score_detailed(self):
        """Test functionality: score detailed."""
        scorer = CompositeScorer()
        scorer.add_scorer(ExactMatchScorer(), weight=2.0)
        scorer.add_scorer(ContainsScorer(), weight=1.0)
        details = scorer.score_detailed("hello", "hello")
        assert "overall" in details
        assert "scorers" in details
        assert len(details["scorers"]) == 2

    def test_scorer_count(self):
        """Test functionality: scorer count."""
        scorer = CompositeScorer()
        assert scorer.scorer_count == 0
        scorer.add_scorer(ExactMatchScorer())
        assert scorer.scorer_count == 1


# ---------------------------------------------------------------------------
# create_default_scorer
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCreateDefaultScorer:
    """Test suite for CreateDefaultScorer."""
    def test_returns_composite(self):
        """Test functionality: returns composite."""
        scorer = create_default_scorer()
        assert isinstance(scorer, CompositeScorer)
        assert scorer.scorer_count == 3

    def test_default_scorer_produces_score(self):
        """Test functionality: default scorer produces score."""
        scorer = create_default_scorer()
        score = scorer.score("hello world", "hello world")
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# BenchmarkCase and BenchmarkResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBenchmarkDataclasses:
    """Test suite for BenchmarkDataclasses."""
    def test_case_auto_id(self):
        """Test functionality: case auto id."""
        case = BenchmarkCase(input_text="hi", expected_output="hello")
        assert len(case.id) > 0

    def test_case_explicit_id(self):
        """Test functionality: case explicit id."""
        case = BenchmarkCase(id="c1", input_text="hi", expected_output="hello")
        assert case.id == "c1"

    def test_result_passed_property(self):
        """Test functionality: result passed property."""
        r_pass = BenchmarkResult(case_id="1", score=0.8, duration_ms=1.0, scorer_name="exact")
        r_fail = BenchmarkResult(case_id="2", score=0.3, duration_ms=1.0, scorer_name="exact")
        assert r_pass.passed is True
        assert r_fail.passed is False

    def test_result_to_dict(self):
        """Test functionality: result to dict."""
        r = BenchmarkResult(case_id="1", score=0.9, duration_ms=5.0, scorer_name="exact")
        d = r.to_dict()
        assert d["case_id"] == "1"
        assert d["passed"] is True


# ---------------------------------------------------------------------------
# BenchmarkSuite and SuiteResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBenchmarkSuite:
    """Test suite for BenchmarkSuite."""
    def test_add_case_and_count(self):
        """Test functionality: add case and count."""
        suite = BenchmarkSuite(name="test")
        suite.add_case(input_text="a", expected_output="b")
        assert suite.case_count == 1

    def test_run_with_identity_model(self):
        """Test functionality: run with identity model."""
        suite = BenchmarkSuite(name="identity", scorer=ExactMatchScorer(case_sensitive=True))
        suite.add_case(input_text="hello", expected_output="hello")
        suite.add_case(input_text="world", expected_output="WORLD")

        result = suite.run(model_fn=lambda x: x)
        assert isinstance(result, SuiteResult)
        assert result.total_cases == 2
        assert result.passed_cases == 1  # "hello" matches exactly, "world" != "WORLD" (case sensitive)

    def test_suite_result_stats(self):
        """Test functionality: suite result stats."""
        suite = BenchmarkSuite(name="stats", scorer=ExactMatchScorer(case_sensitive=False))
        suite.add_case(input_text="a", expected_output="a")
        suite.add_case(input_text="b", expected_output="b")
        result = suite.run(model_fn=lambda x: x)
        assert result.average_score == 1.0
        assert result.pass_rate == 1.0

    def test_suite_remove_case(self):
        """Test functionality: suite remove case."""
        suite = BenchmarkSuite(name="rm")
        case = suite.add_case(input_text="a", expected_output="b")
        assert suite.remove_case(case.id) is True
        assert suite.case_count == 0

    def test_suite_get_cases_by_tag(self):
        """Test functionality: suite get cases by tag."""
        suite = BenchmarkSuite(name="tags")
        suite.add_case(input_text="a", expected_output="b", tags=["math"])
        suite.add_case(input_text="c", expected_output="d", tags=["logic"])
        math_cases = suite.get_cases_by_tag("math")
        assert len(math_cases) == 1

    def test_suite_model_exception_handled(self):
        """Test functionality: suite model exception handled."""
        suite = BenchmarkSuite(name="err", scorer=ContainsScorer())
        suite.add_case(input_text="x", expected_output="x")

        def bad_model(text):
            raise ValueError("broken")

        result = suite.run(model_fn=bad_model)
        assert result.total_cases == 1
        assert result.results[0].actual_output.startswith("ERROR:")

    def test_suite_to_dict(self):
        """Test functionality: suite to dict."""
        suite = BenchmarkSuite(name="dict_test")
        suite.add_case(input_text="a", expected_output="a")
        result = suite.run(model_fn=lambda x: x)
        d = result.to_dict()
        assert d["suite_name"] == "dict_test"
        assert "results" in d


# ---------------------------------------------------------------------------
# QualityAnalyzer and analyze_quality
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestQualityAnalyzer:
    """Test suite for QualityAnalyzer."""
    def test_analyze_nonempty_output(self):
        """Test functionality: analyze nonempty output."""
        analyzer = QualityAnalyzer()
        report = analyzer.analyze(
            "Machine learning is a field of artificial intelligence. "
            "It enables systems to learn from data. "
            "There are many approaches including supervised and unsupervised learning."
        )
        assert isinstance(report, QualityReport)
        assert 0.0 <= report.overall_score <= 1.0
        assert len(report.scores) == 5

    def test_analyze_empty_output(self):
        """Test functionality: analyze empty output."""
        analyzer = QualityAnalyzer()
        report = analyzer.analyze("")
        # Relevance scores 0.5 when no context is provided, so overall is not 0.0
        assert report.overall_score <= 0.15
        assert report.get_score(QualityDimension.COHERENCE) == 0.0
        assert report.get_score(QualityDimension.COMPLETENESS) == 0.0
        assert report.get_score(QualityDimension.CONCISENESS) == 0.0
        assert report.get_score(QualityDimension.ACCURACY) == 0.0

    def test_analyze_with_context(self):
        """Test functionality: analyze with context."""
        analyzer = QualityAnalyzer()
        report = analyzer.analyze(
            "Python is great for machine learning tasks.",
            context="Tell me about Python and machine learning"
        )
        relevance_score = report.get_score(QualityDimension.RELEVANCE)
        assert relevance_score > 0.0

    def test_weakest_and_strongest(self):
        """Test functionality: weakest and strongest."""
        report = analyze_quality(
            "This is a test sentence with some content that is reasonably complete."
        )
        assert report.weakest_dimension is not None
        assert report.strongest_dimension is not None

    def test_quality_report_to_dict(self):
        """Test functionality: quality report to dict."""
        report = analyze_quality("Sample output text for analysis.")
        d = report.to_dict()
        assert "overall_score" in d
        assert "scores" in d
        assert "weakest" in d
        assert "strongest" in d

    def test_dimension_enum_values(self):
        """Test functionality: dimension enum values."""
        assert QualityDimension.COHERENCE.value == "coherence"
        assert QualityDimension.RELEVANCE.value == "relevance"
        assert QualityDimension.COMPLETENESS.value == "completeness"
        assert QualityDimension.CONCISENESS.value == "conciseness"
        assert QualityDimension.ACCURACY.value == "accuracy"

    def test_custom_weights(self):
        """Test functionality: custom weights."""
        weights = {
            QualityDimension.COHERENCE: 2.0,
            QualityDimension.RELEVANCE: 0.0,
            QualityDimension.COMPLETENESS: 1.0,
            QualityDimension.CONCISENESS: 1.0,
            QualityDimension.ACCURACY: 1.0,
        }
        analyzer = QualityAnalyzer(dimension_weights=weights)
        report = analyzer.analyze("Test output.")
        assert isinstance(report.overall_score, float)
