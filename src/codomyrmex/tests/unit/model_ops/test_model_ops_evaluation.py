"""Comprehensive tests for model_ops/evaluation submodule.

Tests cover:
- QualityAnalyzer heuristic scoring across all five dimensions
- QualityReport dataclass accessors, serialization, weakest/strongest
- Scorer protocol implementations (ExactMatch, Contains, Length, Regex, Composite)
- BenchmarkCase, BenchmarkResult, BenchmarkSuite, SuiteResult lifecycle
- Metric classes with real numeric data (parametrized)
- ModelEvaluator orchestration
- Edge cases: empty inputs, single-word outputs, boundary scores
- Serialization round-trips (to_dict)
"""

import json
import math

import pytest

from codomyrmex.model_ops.evaluation import (
    AccuracyMetric,
    AUCROCMetric,
    BenchmarkCase,
    BenchmarkResult,
    BenchmarkSuite,
    CompositeScorer,
    ConfusionMatrix,
    ContainsScorer,
    DimensionScore,
    EvaluationResult,
    ExactMatchScorer,
    F1Metric,
    LengthScorer,
    MAEMetric,
    ModelEvaluator,
    MSEMetric,
    PrecisionMetric,
    QualityAnalyzer,
    QualityDimension,
    QualityReport,
    R2Metric,
    RecallMetric,
    RegexScorer,
    RMSEMetric,
    SuiteResult,
    TaskType,
    WeightedScorer,
    analyze_quality,
    create_default_scorer,
    create_evaluator,
)

# ---------------------------------------------------------------------------
# QualityAnalyzer -- coherence, relevance, completeness, conciseness, accuracy
# ---------------------------------------------------------------------------


class TestQualityAnalyzerCoherence:
    """Tests for the coherence dimension of QualityAnalyzer."""

    @pytest.mark.unit
    def test_coherence_empty_output_scores_zero(self):
        """Empty text must score 0.0 on coherence."""
        qa = QualityAnalyzer()
        report = qa.analyze("")
        assert report.get_score(QualityDimension.COHERENCE) == 0.0

    @pytest.mark.unit
    def test_coherence_single_short_sentence(self):
        """A single short sentence scores proportionally to word count."""
        qa = QualityAnalyzer()
        report = qa.analyze("Hello world.")
        score = report.get_score(QualityDimension.COHERENCE)
        # Two words -> min(1.0, 2/5) = 0.4
        assert abs(score - 0.4) < 1e-5

    @pytest.mark.unit
    def test_coherence_single_long_sentence(self):
        """A single sentence with 5+ words caps coherence at 1.0."""
        qa = QualityAnalyzer()
        report = qa.analyze("The quick brown fox jumps over the lazy dog.")
        score = report.get_score(QualityDimension.COHERENCE)
        assert abs(score - 1.0) < 1e-5

    @pytest.mark.unit
    def test_coherence_multiple_uniform_sentences(self):
        """Multiple sentences with similar lengths score high on coherence."""
        qa = QualityAnalyzer()
        text = (
            "The sun rises early. The birds sing loudly. "
            "The wind blows gently. The day begins anew."
        )
        report = qa.analyze(text)
        score = report.get_score(QualityDimension.COHERENCE)
        # Uniform sentence lengths -> low CV -> high score
        assert score > 0.7

    @pytest.mark.unit
    def test_coherence_repeated_words_penalized(self):
        """Consecutive repeated words reduce coherence score."""
        qa = QualityAnalyzer()
        text = "The the the the cat sat. The the the the dog ran."
        report = qa.analyze(text)
        score = report.get_score(QualityDimension.COHERENCE)
        # Heavy consecutive repetition should drop score
        assert score < 0.8


class TestQualityAnalyzerRelevance:
    """Tests for the relevance dimension."""

    @pytest.mark.unit
    def test_relevance_no_context_neutral(self):
        """Without context, relevance defaults to 0.5."""
        qa = QualityAnalyzer()
        report = qa.analyze("Some output text.")
        assert report.get_score(QualityDimension.RELEVANCE) == 0.5

    @pytest.mark.unit
    def test_relevance_empty_output_zero(self):
        """Empty output with context scores 0.0 relevance."""
        qa = QualityAnalyzer()
        report = qa.analyze("", context="machine learning algorithms")
        assert report.get_score(QualityDimension.RELEVANCE) == 0.0

    @pytest.mark.unit
    def test_relevance_high_overlap(self):
        """Output containing many context keywords scores high relevance."""
        qa = QualityAnalyzer()
        context = "neural network training optimization gradient"
        output = "The neural network uses gradient optimization during training."
        report = qa.analyze(output, context=context)
        score = report.get_score(QualityDimension.RELEVANCE)
        assert score > 0.8

    @pytest.mark.unit
    def test_relevance_no_overlap(self):
        """Output with no keyword overlap with context scores low."""
        qa = QualityAnalyzer()
        context = "quantum physics entanglement superposition"
        output = "The cat sat on the mat drinking milk."
        report = qa.analyze(output, context=context)
        score = report.get_score(QualityDimension.RELEVANCE)
        assert score < 0.3

    @pytest.mark.unit
    def test_relevance_stopword_only_context(self):
        """Context with only stopwords returns neutral 0.5."""
        qa = QualityAnalyzer()
        report = qa.analyze("Some text here.", context="the a an is are")
        assert report.get_score(QualityDimension.RELEVANCE) == 0.5


class TestQualityAnalyzerCompleteness:
    """Tests for the completeness dimension."""

    @pytest.mark.unit
    def test_completeness_empty_zero(self):
        """Empty output scores 0.0 completeness."""
        qa = QualityAnalyzer()
        report = qa.analyze("")
        assert report.get_score(QualityDimension.COMPLETENESS) == 0.0

    @pytest.mark.unit
    def test_completeness_ends_with_period(self):
        """Text ending with a period gets a completeness bonus."""
        qa = QualityAnalyzer()
        text = "In conclusion, the results demonstrate a clear improvement in performance."
        report = qa.analyze(text)
        score = report.get_score(QualityDimension.COMPLETENESS)
        assert score > 0.5

    @pytest.mark.unit
    def test_completeness_incompletion_markers_penalized(self):
        """Text with TODO or TBD markers gets penalized."""
        qa = QualityAnalyzer()
        text = "The analysis is partially done... TODO: finish the rest. TBD."
        report = qa.analyze(text)
        score = report.get_score(QualityDimension.COMPLETENESS)
        # Has incompletion markers, so score should be lower
        report_clean = qa.analyze(
            "The analysis is fully completed and verified."
        )
        score_clean = report_clean.get_score(QualityDimension.COMPLETENESS)
        assert score < score_clean


class TestQualityAnalyzerConciseness:
    """Tests for the conciseness dimension."""

    @pytest.mark.unit
    def test_conciseness_empty_zero(self):
        """Empty output scores 0.0 conciseness."""
        qa = QualityAnalyzer()
        report = qa.analyze("")
        assert report.get_score(QualityDimension.CONCISENESS) == 0.0

    @pytest.mark.unit
    def test_conciseness_high_unique_ratio(self):
        """Text with many unique words scores high conciseness."""
        qa = QualityAnalyzer()
        text = "Every word here is unique different special novel."
        report = qa.analyze(text)
        score = report.get_score(QualityDimension.CONCISENESS)
        assert score > 0.7

    @pytest.mark.unit
    def test_conciseness_repetitive_text_lower(self):
        """Highly repetitive text scores lower conciseness."""
        qa = QualityAnalyzer()
        text = "cat cat cat cat cat cat cat cat cat cat"
        report = qa.analyze(text)
        score = report.get_score(QualityDimension.CONCISENESS)
        assert score < 0.5


class TestQualityAnalyzerAccuracy:
    """Tests for the accuracy dimension."""

    @pytest.mark.unit
    def test_accuracy_empty_zero(self):
        """Empty output scores 0.0 accuracy."""
        qa = QualityAnalyzer()
        report = qa.analyze("")
        assert report.get_score(QualityDimension.ACCURACY) == 0.0

    @pytest.mark.unit
    def test_accuracy_factual_density_boosts(self):
        """Text with numbers and proper nouns scores higher on accuracy."""
        qa = QualityAnalyzer()
        text = "Albert Einstein published 300 papers. In 1905, he introduced Special Relativity (Einstein 1905)."
        report = qa.analyze(text)
        score = report.get_score(QualityDimension.ACCURACY)
        assert score > 0.5

    @pytest.mark.unit
    def test_accuracy_hedging_penalized(self):
        """Excessive hedging words reduce accuracy score."""
        qa = QualityAnalyzer()
        text_hedged = "Maybe the result could possibly perhaps seem right."
        text_firm = "The result is correct and verified."
        report_hedged = qa.analyze(text_hedged)
        report_firm = qa.analyze(text_firm)
        assert report_hedged.get_score(QualityDimension.ACCURACY) < report_firm.get_score(QualityDimension.ACCURACY)

    @pytest.mark.unit
    def test_accuracy_context_overlap_bonus(self):
        """Providing context with factual overlap boosts accuracy."""
        qa = QualityAnalyzer()
        context = "Python programming language Guido van Rossum"
        output = "Python was created by Guido van Rossum in 1991."
        report_with_ctx = qa.analyze(output, context=context)
        report_no_ctx = qa.analyze(output, context="")
        assert report_with_ctx.get_score(QualityDimension.ACCURACY) >= report_no_ctx.get_score(QualityDimension.ACCURACY)


# ---------------------------------------------------------------------------
# QualityReport dataclass
# ---------------------------------------------------------------------------


class TestQualityReport:
    """Tests for QualityReport accessors and serialization."""

    @pytest.mark.unit
    def test_quality_report_overall_score(self):
        """analyze_quality returns a report with a valid overall_score."""
        report = analyze_quality("The quick brown fox jumps over the lazy dog.")
        assert 0.0 <= report.overall_score <= 1.0

    @pytest.mark.unit
    def test_quality_report_weakest_strongest(self):
        """weakest_dimension and strongest_dimension are valid dimensions."""
        report = analyze_quality(
            "Python is a versatile programming language used worldwide.",
            context="programming language"
        )
        assert report.weakest_dimension in QualityDimension
        assert report.strongest_dimension in QualityDimension

    @pytest.mark.unit
    def test_quality_report_empty_has_no_weakest(self):
        """An empty QualityReport has None for weakest/strongest."""
        report = QualityReport()
        assert report.weakest_dimension is None
        assert report.strongest_dimension is None

    @pytest.mark.unit
    def test_quality_report_to_dict_structure(self):
        """to_dict returns expected top-level keys."""
        report = analyze_quality("Hello world.")
        d = report.to_dict()
        assert "overall_score" in d
        assert "scores" in d
        assert "weakest" in d
        assert "strongest" in d
        assert "metadata" in d

    @pytest.mark.unit
    def test_quality_report_to_dict_roundtrip_json(self):
        """to_dict output is JSON-serializable."""
        report = analyze_quality("Testing JSON serialization.")
        d = report.to_dict()
        serialized = json.dumps(d)
        deserialized = json.loads(serialized)
        assert deserialized["overall_score"] == d["overall_score"]

    @pytest.mark.unit
    def test_quality_report_get_explanation(self):
        """get_explanation returns a non-empty string for scored dimensions."""
        report = analyze_quality("The model produces high quality output.")
        for dim in QualityDimension:
            explanation = report.get_explanation(dim)
            assert isinstance(explanation, str)
            assert len(explanation) > 0

    @pytest.mark.unit
    def test_quality_report_get_score_missing_dimension(self):
        """get_score returns 0.0 for a dimension not in the report."""
        report = QualityReport()
        assert report.get_score(QualityDimension.COHERENCE) == 0.0

    @pytest.mark.unit
    def test_quality_report_custom_weights(self):
        """Custom dimension weights affect the overall score."""
        # Weight coherence very heavily, zero out everything else
        weights = {
            QualityDimension.COHERENCE: 10.0,
            QualityDimension.RELEVANCE: 0.0,
            QualityDimension.COMPLETENESS: 0.0,
            QualityDimension.CONCISENESS: 0.0,
            QualityDimension.ACCURACY: 0.0,
        }
        qa = QualityAnalyzer(dimension_weights=weights)
        report = qa.analyze("The quick brown fox jumps over the lazy dog.")
        # Overall should be dominated by coherence
        coherence_score = report.get_score(QualityDimension.COHERENCE)
        assert abs(report.overall_score - coherence_score) < 1e-5


# ---------------------------------------------------------------------------
# Scorers
# ---------------------------------------------------------------------------


class TestExactMatchScorer:
    """Tests for ExactMatchScorer."""

    @pytest.mark.unit
    def test_exact_match_identical(self):
        """Identical strings score 1.0."""
        scorer = ExactMatchScorer()
        assert scorer.score("hello", "hello") == 1.0

    @pytest.mark.unit
    def test_exact_match_case_sensitive(self):
        """Case-sensitive mode distinguishes case."""
        scorer = ExactMatchScorer(case_sensitive=True)
        assert scorer.score("Hello", "hello") == 0.0

    @pytest.mark.unit
    def test_exact_match_case_insensitive(self):
        """Case-insensitive mode ignores case."""
        scorer = ExactMatchScorer(case_sensitive=False)
        assert scorer.score("Hello", "hello") == 1.0

    @pytest.mark.unit
    def test_exact_match_strips_whitespace(self):
        """Whitespace stripping is enabled by default."""
        scorer = ExactMatchScorer()
        assert scorer.score("  hello  ", "hello") == 1.0

    @pytest.mark.unit
    def test_exact_match_batch(self):
        """score_batch returns correct list of scores."""
        scorer = ExactMatchScorer(case_sensitive=False)
        pairs = [("hello", "hello"), ("world", "WORLD"), ("foo", "bar")]
        scores = scorer.score_batch(pairs)
        assert scores == [1.0, 1.0, 0.0]


class TestContainsScorer:
    """Tests for ContainsScorer."""

    @pytest.mark.unit
    def test_contains_substring(self):
        """Output containing reference as substring scores 1.0."""
        scorer = ContainsScorer()
        assert scorer.score("hello world", "world") == 1.0

    @pytest.mark.unit
    def test_contains_no_match(self):
        """Output not containing reference scores 0.0."""
        scorer = ContainsScorer()
        assert scorer.score("hello world", "xyz") == 0.0

    @pytest.mark.unit
    def test_contains_case_insensitive(self):
        """Case-insensitive contains checks."""
        scorer = ContainsScorer(case_sensitive=False)
        assert scorer.score("Hello World", "hello") == 1.0


class TestLengthScorer:
    """Tests for LengthScorer."""

    @pytest.mark.unit
    def test_length_within_range(self):
        """Output within range scores 1.0."""
        scorer = LengthScorer(min_length=3, max_length=10)
        assert scorer.score("hello") == 1.0

    @pytest.mark.unit
    def test_length_below_range(self):
        """Output shorter than min scores less than 1.0."""
        scorer = LengthScorer(min_length=10, max_length=20)
        score = scorer.score("hi")
        assert 0.0 <= score < 1.0

    @pytest.mark.unit
    def test_length_above_range(self):
        """Output longer than max scores less than 1.0."""
        scorer = LengthScorer(min_length=1, max_length=5)
        score = scorer.score("a very long string indeed")
        assert 0.0 <= score < 1.0

    @pytest.mark.unit
    def test_length_invalid_min_raises(self):
        """Negative min_length raises ValueError."""
        with pytest.raises(ValueError):
            LengthScorer(min_length=-1, max_length=10)

    @pytest.mark.unit
    def test_length_max_less_than_min_raises(self):
        """max_length < min_length raises ValueError."""
        with pytest.raises(ValueError):
            LengthScorer(min_length=10, max_length=5)


class TestRegexScorer:
    """Tests for RegexScorer."""

    @pytest.mark.unit
    def test_regex_search_match(self):
        """Pattern found somewhere in output scores 1.0."""
        scorer = RegexScorer()
        assert scorer.score("the answer is 42", r"\d+") == 1.0

    @pytest.mark.unit
    def test_regex_search_no_match(self):
        """Pattern not found scores 0.0."""
        scorer = RegexScorer()
        assert scorer.score("no numbers here", r"\d+") == 0.0

    @pytest.mark.unit
    def test_regex_full_match(self):
        """Full match mode requires entire string to match."""
        scorer = RegexScorer(full_match=True)
        assert scorer.score("42", r"\d+") == 1.0
        assert scorer.score("answer 42", r"\d+") == 0.0

    @pytest.mark.unit
    def test_regex_invalid_pattern(self):
        """Invalid regex pattern returns 0.0 instead of crashing."""
        scorer = RegexScorer()
        assert scorer.score("test", r"[invalid") == 0.0


class TestCompositeScorer:
    """Tests for CompositeScorer and WeightedScorer."""

    @pytest.mark.unit
    def test_composite_empty_scores_zero(self):
        """Composite with no scorers returns 0.0."""
        scorer = CompositeScorer()
        assert scorer.score("a", "b") == 0.0

    @pytest.mark.unit
    def test_composite_weighted_average(self):
        """Composite correctly computes weighted average."""
        scorer = CompositeScorer([
            WeightedScorer(ExactMatchScorer(case_sensitive=False), weight=2.0),
            WeightedScorer(ContainsScorer(), weight=1.0),
        ])
        # "hello" vs "hello" => exact=1.0 (w=2), contains=1.0 (w=1)
        # weighted avg = (2*1.0 + 1*1.0) / 3 = 1.0
        assert scorer.score("hello", "hello") == 1.0

    @pytest.mark.unit
    def test_composite_add_scorer_chaining(self):
        """add_scorer returns self for method chaining."""
        scorer = CompositeScorer()
        result = scorer.add_scorer(ExactMatchScorer(), weight=1.0)
        assert result is scorer
        assert scorer.scorer_count == 1

    @pytest.mark.unit
    def test_composite_add_scorer_zero_weight_raises(self):
        """Adding a scorer with non-positive weight raises ValueError."""
        scorer = CompositeScorer()
        with pytest.raises(ValueError, match="positive"):
            scorer.add_scorer(ExactMatchScorer(), weight=0.0)

    @pytest.mark.unit
    def test_composite_score_detailed(self):
        """score_detailed returns per-scorer breakdown."""
        scorer = CompositeScorer([
            WeightedScorer(ExactMatchScorer(case_sensitive=False), weight=1.0),
            WeightedScorer(ContainsScorer(), weight=1.0),
        ])
        details = scorer.score_detailed("hello world", "hello")
        assert "overall" in details
        assert len(details["scorers"]) == 2
        for s in details["scorers"]:
            assert "name" in s
            assert "score" in s
            assert "weight" in s

    @pytest.mark.unit
    def test_create_default_scorer_structure(self):
        """create_default_scorer returns a CompositeScorer with 3 sub-scorers."""
        scorer = create_default_scorer()
        assert isinstance(scorer, CompositeScorer)
        assert scorer.scorer_count == 3


# ---------------------------------------------------------------------------
# BenchmarkCase / BenchmarkResult / BenchmarkSuite / SuiteResult
# ---------------------------------------------------------------------------


class TestBenchmarkCase:
    """Tests for BenchmarkCase dataclass."""

    @pytest.mark.unit
    def test_case_auto_id(self):
        """BenchmarkCase generates an ID when none provided."""
        case = BenchmarkCase(input_text="hello", expected_output="world")
        assert case.id != ""
        assert len(case.id) == 8

    @pytest.mark.unit
    def test_case_explicit_id(self):
        """BenchmarkCase uses explicit ID when provided."""
        case = BenchmarkCase(input_text="a", expected_output="b", id="custom-1")
        assert case.id == "custom-1"

    @pytest.mark.unit
    def test_case_tags_and_metadata(self):
        """BenchmarkCase stores tags and metadata."""
        case = BenchmarkCase(
            input_text="x", expected_output="y",
            metadata={"difficulty": "hard"},
            tags=["math", "algebra"],
        )
        assert case.metadata["difficulty"] == "hard"
        assert "math" in case.tags


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass."""

    @pytest.mark.unit
    def test_result_passed_threshold(self):
        """passed is True when score >= 0.5."""
        result = BenchmarkResult(
            case_id="c1", score=0.7, duration_ms=10.0, scorer_name="exact"
        )
        assert result.passed is True

    @pytest.mark.unit
    def test_result_failed_threshold(self):
        """passed is False when score < 0.5."""
        result = BenchmarkResult(
            case_id="c1", score=0.3, duration_ms=10.0, scorer_name="exact"
        )
        assert result.passed is False

    @pytest.mark.unit
    def test_result_to_dict(self):
        """to_dict returns all expected keys."""
        result = BenchmarkResult(
            case_id="c1", score=0.9, duration_ms=5.0,
            scorer_name="exact", actual_output="hello",
        )
        d = result.to_dict()
        assert d["case_id"] == "c1"
        assert d["score"] == 0.9
        assert d["passed"] is True
        assert "duration_ms" in d
        assert "scorer_name" in d


class TestBenchmarkSuite:
    """Tests for BenchmarkSuite lifecycle."""

    @pytest.mark.unit
    def test_suite_add_case(self):
        """add_case increases case count."""
        suite = BenchmarkSuite(name="test-suite")
        suite.add_case("hello", "world")
        assert suite.case_count == 1

    @pytest.mark.unit
    def test_suite_add_cases_bulk(self):
        """add_cases adds multiple cases at once."""
        suite = BenchmarkSuite(name="bulk")
        cases = [
            BenchmarkCase(input_text="a", expected_output="a"),
            BenchmarkCase(input_text="b", expected_output="b"),
        ]
        suite.add_cases(cases)
        assert suite.case_count == 2

    @pytest.mark.unit
    def test_suite_remove_case(self):
        """remove_case removes by ID and returns True."""
        suite = BenchmarkSuite()
        suite.add_case("x", "y", case_id="rm-1")
        assert suite.remove_case("rm-1") is True
        assert suite.case_count == 0

    @pytest.mark.unit
    def test_suite_remove_case_not_found(self):
        """remove_case returns False for unknown ID."""
        suite = BenchmarkSuite()
        assert suite.remove_case("nonexistent") is False

    @pytest.mark.unit
    def test_suite_get_cases_by_tag(self):
        """get_cases_by_tag filters correctly."""
        suite = BenchmarkSuite()
        suite.add_case("a", "b", tags=["math"])
        suite.add_case("c", "d", tags=["english"])
        suite.add_case("e", "f", tags=["math", "hard"])
        math_cases = suite.get_cases_by_tag("math")
        assert len(math_cases) == 2

    @pytest.mark.unit
    def test_suite_clear(self):
        """clear removes all cases."""
        suite = BenchmarkSuite()
        suite.add_case("a", "b")
        suite.add_case("c", "d")
        suite.clear()
        assert suite.case_count == 0

    @pytest.mark.unit
    def test_suite_run_with_identity_function(self):
        """Running suite with identity model_fn and exact match scorer."""
        suite = BenchmarkSuite(
            name="identity-test",
            scorer=ExactMatchScorer(case_sensitive=False),
        )
        suite.add_case("hello", "hello")
        suite.add_case("world", "WORLD")
        suite.add_case("foo", "bar")

        result = suite.run(model_fn=lambda x: x)
        assert isinstance(result, SuiteResult)
        assert result.total_cases == 3
        assert result.passed_cases == 2  # hello matches, world matches (case-insensitive), foo != bar
        assert result.failed_cases == 1
        assert result.average_score == pytest.approx(2.0 / 3.0, abs=1e-5)
        assert 0.0 < result.pass_rate < 1.0

    @pytest.mark.unit
    def test_suite_run_model_fn_error_handled(self):
        """Suite handles model_fn that raises an exception."""
        suite = BenchmarkSuite(name="error-test")
        suite.add_case("trigger", "expected")

        def failing_model(text):
            raise RuntimeError("model crashed")

        result = suite.run(model_fn=failing_model)
        assert result.total_cases == 1
        # Error output won't match expected, so score should be 0.0
        assert result.results[0].score == 0.0

    @pytest.mark.unit
    def test_suite_run_scorer_override(self):
        """Suite run accepts a scorer override."""
        suite = BenchmarkSuite(
            name="override-test",
            scorer=ExactMatchScorer(case_sensitive=True),
        )
        suite.add_case("hello", "hello")

        # Override with contains scorer -- "hello" contains "hello"
        result = suite.run(
            model_fn=lambda x: x,
            scorer=ContainsScorer(),
        )
        assert result.results[0].scorer_name == "contains"
        assert result.results[0].score == 1.0

    @pytest.mark.unit
    def test_suite_get_results_convenience(self):
        """get_results returns just the list of BenchmarkResult."""
        suite = BenchmarkSuite(name="conv")
        suite.add_case("a", "a")
        results = suite.get_results(model_fn=lambda x: x)
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], BenchmarkResult)


class TestSuiteResult:
    """Tests for SuiteResult aggregation and serialization."""

    @pytest.mark.unit
    def test_suite_result_empty(self):
        """Empty SuiteResult has sensible defaults."""
        sr = SuiteResult(suite_name="empty")
        assert sr.total_cases == 0
        assert sr.average_score == 0.0
        assert sr.pass_rate == 0.0

    @pytest.mark.unit
    def test_suite_result_get_result_by_id(self):
        """get_result retrieves by case_id."""
        sr = SuiteResult(
            suite_name="test",
            results=[
                BenchmarkResult(case_id="a", score=1.0, duration_ms=1.0, scorer_name="em"),
                BenchmarkResult(case_id="b", score=0.0, duration_ms=2.0, scorer_name="em"),
            ],
        )
        assert sr.get_result("a").score == 1.0
        assert sr.get_result("c") is None

    @pytest.mark.unit
    def test_suite_result_to_dict_keys(self):
        """to_dict returns all expected top-level keys."""
        sr = SuiteResult(
            suite_name="s1",
            results=[
                BenchmarkResult(case_id="x", score=0.8, duration_ms=5.0, scorer_name="em"),
            ],
        )
        d = sr.to_dict()
        expected_keys = {
            "suite_name", "total_cases", "passed_cases", "failed_cases",
            "average_score", "pass_rate", "total_duration_ms", "results", "metadata",
        }
        assert set(d.keys()) == expected_keys

    @pytest.mark.unit
    def test_suite_result_json_serializable(self):
        """SuiteResult.to_dict() output is JSON-serializable."""
        sr = SuiteResult(
            suite_name="json-test",
            results=[
                BenchmarkResult(case_id="j1", score=0.5, duration_ms=3.0, scorer_name="em"),
            ],
        )
        serialized = json.dumps(sr.to_dict())
        assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# Metric classes -- parametrized with real numeric data
# ---------------------------------------------------------------------------


class TestMetricsParametrized:
    """Parametrized tests for classification and regression metrics."""

    @pytest.mark.unit
    @pytest.mark.parametrize("y_true,y_pred,expected_accuracy", [
        ([1, 1, 1, 1], [1, 1, 1, 1], 1.0),
        ([1, 0, 1, 0], [0, 1, 0, 1], 0.0),
        ([1, 0, 1, 0, 1], [1, 0, 0, 0, 1], 0.8),
    ])
    def test_accuracy_parametrized(self, y_true, y_pred, expected_accuracy):
        """Accuracy metric across multiple scenarios."""
        metric = AccuracyMetric()
        assert abs(metric.compute(y_true, y_pred) - expected_accuracy) < 1e-9

    @pytest.mark.unit
    @pytest.mark.parametrize("y_true,y_pred,expected_precision", [
        ([1, 1, 0, 0], [1, 1, 1, 0], 2.0 / 3.0),   # TP=2, FP=1
        ([1, 1, 0, 0], [0, 0, 0, 0], 0.0),           # No positive predictions
        ([1, 1, 0, 0], [1, 1, 0, 0], 1.0),            # Perfect
    ])
    def test_precision_parametrized(self, y_true, y_pred, expected_precision):
        """Precision metric across multiple scenarios."""
        metric = PrecisionMetric(positive_class=1)
        assert abs(metric.compute(y_true, y_pred) - expected_precision) < 1e-9

    @pytest.mark.unit
    @pytest.mark.parametrize("y_true,y_pred,expected_recall", [
        ([1, 1, 0, 0], [1, 0, 0, 0], 0.5),          # TP=1, FN=1
        ([1, 1, 1, 0], [1, 1, 1, 0], 1.0),           # Perfect recall
        ([0, 0, 0, 0], [1, 1, 1, 1], 0.0),           # No actual positives
    ])
    def test_recall_parametrized(self, y_true, y_pred, expected_recall):
        """Recall metric across multiple scenarios."""
        metric = RecallMetric(positive_class=1)
        assert abs(metric.compute(y_true, y_pred) - expected_recall) < 1e-9

    @pytest.mark.unit
    @pytest.mark.parametrize("y_true,y_pred,expected_f1", [
        ([1, 1, 0, 0], [1, 1, 0, 0], 1.0),           # Perfect
        ([1, 1, 0, 0], [0, 0, 1, 1], 0.0),            # All wrong
        ([1, 0, 1, 0], [1, 0, 0, 1], 0.5),            # TP=1, FP=1, FN=1 -> P=0.5, R=0.5 -> F1=0.5
    ])
    def test_f1_parametrized(self, y_true, y_pred, expected_f1):
        """F1 metric across multiple scenarios."""
        metric = F1Metric(positive_class=1)
        assert abs(metric.compute(y_true, y_pred) - expected_f1) < 1e-9

    @pytest.mark.unit
    @pytest.mark.parametrize("y_true,y_pred,expected_mse", [
        ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], 0.0),
        ([0.0, 0.0], [1.0, 1.0], 1.0),
        ([1.0, 3.0, 5.0], [2.0, 4.0, 6.0], 1.0),
    ])
    def test_mse_parametrized(self, y_true, y_pred, expected_mse):
        """MSE across multiple regression scenarios."""
        metric = MSEMetric()
        assert abs(metric.compute(y_true, y_pred) - expected_mse) < 1e-9

    @pytest.mark.unit
    @pytest.mark.parametrize("y_true,y_pred,expected_mae", [
        ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], 0.0),
        ([0.0, 0.0], [1.0, -1.0], 1.0),
        ([10.0, 20.0], [12.0, 18.0], 2.0),
    ])
    def test_mae_parametrized(self, y_true, y_pred, expected_mae):
        """MAE across multiple regression scenarios."""
        metric = MAEMetric()
        assert abs(metric.compute(y_true, y_pred) - expected_mae) < 1e-9

    @pytest.mark.unit
    @pytest.mark.parametrize("y_true,y_pred,expected_r2", [
        ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0], 1.0),
        ([1.0, 2.0, 3.0], [2.0, 2.0, 2.0], 0.0),
    ])
    def test_r2_parametrized(self, y_true, y_pred, expected_r2):
        """R2 across regression scenarios."""
        metric = R2Metric()
        assert abs(metric.compute(y_true, y_pred) - expected_r2) < 1e-9

    @pytest.mark.unit
    def test_rmse_is_sqrt_of_mse(self):
        """RMSE equals sqrt(MSE) for the same inputs."""
        y_true = [1.0, 2.0, 3.0, 4.0]
        y_pred = [1.1, 2.2, 2.8, 4.5]
        mse_val = MSEMetric().compute(y_true, y_pred)
        rmse_val = RMSEMetric().compute(y_true, y_pred)
        assert abs(rmse_val - math.sqrt(mse_val)) < 1e-9

    @pytest.mark.unit
    def test_auc_roc_random_ordering(self):
        """AUC-ROC with random-ish scores falls between 0 and 1."""
        metric = AUCROCMetric()
        y_true = [1, 0, 1, 0, 1, 0]
        y_scores = [0.9, 0.4, 0.65, 0.2, 0.8, 0.5]
        score = metric.compute(y_true, y_scores)
        assert 0.0 <= score <= 1.0

    @pytest.mark.unit
    def test_auc_roc_no_positives(self):
        """AUC-ROC with no positive labels returns 0.0."""
        metric = AUCROCMetric()
        assert metric.compute([0, 0, 0], [0.5, 0.6, 0.7]) == 0.0

    @pytest.mark.unit
    def test_auc_roc_tied_scores(self):
        """AUC-ROC with tied scores counts 0.5 per tie."""
        metric = AUCROCMetric()
        y_true = [1, 0]
        y_scores = [0.5, 0.5]  # Tied: count += 0.5, total=1
        assert metric.compute(y_true, y_scores) == 0.5


# ---------------------------------------------------------------------------
# ConfusionMatrix extended
# ---------------------------------------------------------------------------


class TestConfusionMatrixExtended:
    """Extended tests for ConfusionMatrix."""

    @pytest.mark.unit
    def test_confusion_matrix_multiclass(self):
        """ConfusionMatrix works with 3+ classes."""
        y_true = [0, 1, 2, 0, 1, 2]
        y_pred = [0, 2, 1, 0, 1, 2]
        cm = ConfusionMatrix(y_true, y_pred)
        assert cm.classes == [0, 1, 2]
        assert cm.get_cell(0, 0) == 2  # correct class 0
        assert cm.get_cell(1, 2) == 1  # class 1 predicted as 2
        assert cm.get_cell(2, 1) == 1  # class 2 predicted as 1

    @pytest.mark.unit
    def test_confusion_matrix_cell_missing_returns_zero(self):
        """get_cell returns 0 for combinations not observed."""
        cm = ConfusionMatrix([0, 1], [0, 1])
        assert cm.get_cell(0, 1) == 0

    @pytest.mark.unit
    def test_confusion_matrix_to_dict_matrix_shape(self):
        """to_dict matrix is square with correct dimensions."""
        cm = ConfusionMatrix([0, 1, 2], [0, 1, 2])
        d = cm.to_dict()
        assert len(d["matrix"]) == 3
        for row in d["matrix"]:
            assert len(row) == 3


# ---------------------------------------------------------------------------
# ModelEvaluator and create_evaluator
# ---------------------------------------------------------------------------


class TestModelEvaluatorExtended:
    """Extended tests for ModelEvaluator."""

    @pytest.mark.unit
    def test_evaluator_multiclass(self):
        """ModelEvaluator works with multiclass task type."""
        evaluator = ModelEvaluator(TaskType.MULTICLASS_CLASSIFICATION)
        result = evaluator.evaluate([0, 1, 2, 0], [0, 1, 2, 1])
        assert "accuracy" in result.metrics
        assert result.metrics["accuracy"] == 0.75

    @pytest.mark.unit
    def test_evaluator_regression_perfect(self):
        """Regression evaluator produces 0 error for perfect predictions."""
        evaluator = create_evaluator("regression")
        result = evaluator.evaluate([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert result.metrics["mse"] == 0.0
        assert result.metrics["mae"] == 0.0
        assert result.metrics["rmse"] == 0.0
        assert abs(result.metrics["r2"] - 1.0) < 1e-9

    @pytest.mark.unit
    def test_evaluation_result_to_dict_metadata(self):
        """EvaluationResult.to_dict includes metadata."""
        result = EvaluationResult(
            metrics={"accuracy": 0.95},
            task_type=TaskType.BINARY_CLASSIFICATION,
            sample_count=200,
            metadata={"model": "test-v1"},
        )
        d = result.to_dict()
        assert d["metadata"]["model"] == "test-v1"

    @pytest.mark.unit
    def test_create_evaluator_multiclass(self):
        """create_evaluator handles 'multiclass' string."""
        evaluator = create_evaluator("multiclass")
        assert evaluator.task_type == TaskType.MULTICLASS_CLASSIFICATION

    @pytest.mark.unit
    def test_create_evaluator_invalid_raises(self):
        """create_evaluator raises ValueError for invalid task type."""
        with pytest.raises(ValueError, match="Unknown task type"):
            create_evaluator("unsupervised")


# ---------------------------------------------------------------------------
# DimensionScore dataclass
# ---------------------------------------------------------------------------


class TestDimensionScore:
    """Tests for the DimensionScore dataclass."""

    @pytest.mark.unit
    def test_dimension_score_defaults(self):
        """DimensionScore has correct defaults."""
        ds = DimensionScore(dimension=QualityDimension.COHERENCE, score=0.8)
        assert ds.explanation == ""
        assert ds.raw_metrics == {}

    @pytest.mark.unit
    def test_dimension_score_with_raw_metrics(self):
        """DimensionScore stores raw_metrics."""
        ds = DimensionScore(
            dimension=QualityDimension.ACCURACY,
            score=0.9,
            explanation="High factual density.",
            raw_metrics={"factual_signals": 5, "hedge_count": 0},
        )
        assert ds.raw_metrics["factual_signals"] == 5
