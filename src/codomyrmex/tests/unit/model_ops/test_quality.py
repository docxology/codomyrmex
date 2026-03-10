"""Comprehensive tests for model_ops.evaluation.quality — zero-mock.

Covers: QualityDimension enum, DimensionScore, QualityReport (get_score,
get_explanation, weakest/strongest, to_dict), QualityAnalyzer (analyze,
_score_coherence, _score_relevance, _score_completeness, _score_conciseness,
_score_accuracy), and helper functions _tokenize, _split_sentences.
"""


from codomyrmex.model_ops.evaluation.quality import (
    DimensionScore,
    QualityAnalyzer,
    QualityDimension,
    QualityReport,
)

# ---------------------------------------------------------------------------
# QualityDimension enum
# ---------------------------------------------------------------------------


class TestQualityDimension:
    def test_values(self):
        assert QualityDimension.COHERENCE.value == "coherence"
        assert QualityDimension.RELEVANCE.value == "relevance"
        assert QualityDimension.COMPLETENESS.value == "completeness"
        assert QualityDimension.CONCISENESS.value == "conciseness"
        assert QualityDimension.ACCURACY.value == "accuracy"

    def test_all_members(self):
        assert len(QualityDimension) == 5


# ---------------------------------------------------------------------------
# DimensionScore
# ---------------------------------------------------------------------------


class TestDimensionScore:
    def test_create(self):
        ds = DimensionScore(dimension=QualityDimension.COHERENCE, score=0.85)
        assert ds.score == 0.85
        assert ds.explanation == ""

    def test_with_explanation(self):
        ds = DimensionScore(
            dimension=QualityDimension.RELEVANCE,
            score=0.7,
            explanation="Good keyword overlap",
        )
        assert "keyword" in ds.explanation


# ---------------------------------------------------------------------------
# QualityReport
# ---------------------------------------------------------------------------


class TestQualityReport:
    def _make_report(self):
        scores = {
            QualityDimension.COHERENCE: DimensionScore(
                dimension=QualityDimension.COHERENCE, score=0.9
            ),
            QualityDimension.RELEVANCE: DimensionScore(
                dimension=QualityDimension.RELEVANCE, score=0.5
            ),
            QualityDimension.COMPLETENESS: DimensionScore(
                dimension=QualityDimension.COMPLETENESS, score=0.7
            ),
        }
        return QualityReport(scores=scores, overall_score=0.7)

    def test_get_score(self):
        report = self._make_report()
        assert report.get_score(QualityDimension.COHERENCE) == 0.9

    def test_get_score_missing(self):
        report = self._make_report()
        assert report.get_score(QualityDimension.ACCURACY) == 0.0

    def test_get_explanation(self):
        report = self._make_report()
        assert isinstance(report.get_explanation(QualityDimension.COHERENCE), str)

    def test_weakest_dimension(self):
        report = self._make_report()
        weakest = report.weakest_dimension
        assert weakest == QualityDimension.RELEVANCE

    def test_strongest_dimension(self):
        report = self._make_report()
        strongest = report.strongest_dimension
        assert strongest == QualityDimension.COHERENCE

    def test_to_dict(self):
        report = self._make_report()
        d = report.to_dict()
        assert isinstance(d, dict)
        assert "overall_score" in d


# ---------------------------------------------------------------------------
# QualityAnalyzer
# ---------------------------------------------------------------------------


class TestQualityAnalyzer:
    def test_default_init(self):
        analyzer = QualityAnalyzer()
        assert analyzer is not None

    def test_custom_weights(self):
        weights = {QualityDimension.COHERENCE: 2.0, QualityDimension.RELEVANCE: 1.0}
        analyzer = QualityAnalyzer(dimension_weights=weights)
        assert analyzer is not None

    def test_analyze_returns_report(self):
        analyzer = QualityAnalyzer()
        report = analyzer.analyze("This is a well-structured response with clear information.")
        assert isinstance(report, QualityReport)
        assert 0.0 <= report.overall_score <= 1.0

    def test_analyze_all_dimensions_scored(self):
        analyzer = QualityAnalyzer()
        report = analyzer.analyze(
            "The Python programming language is versatile and widely used. "
            "It supports multiple paradigms including object-oriented and functional programming."
        )
        for dim in QualityDimension:
            score = report.get_score(dim)
            assert 0.0 <= score <= 1.0, f"{dim.value} score out of range: {score}"

    def test_analyze_with_context(self):
        analyzer = QualityAnalyzer()
        report = analyzer.analyze(
            output="Python is a programming language created by Guido van Rossum.",
            context="Tell me about the Python programming language.",
        )
        assert isinstance(report, QualityReport)

    def test_coherent_text_scores_well(self):
        analyzer = QualityAnalyzer()
        coherent = (
            "Machine learning is a subset of artificial intelligence. "
            "It enables computers to learn from data. "
            "Deep learning is a further specialization. "
            "Neural networks form the backbone of deep learning."
        )
        report = analyzer.analyze(coherent)
        assert report.get_score(QualityDimension.COHERENCE) > 0.3

    def test_empty_output_handled(self):
        analyzer = QualityAnalyzer()
        report = analyzer.analyze("")
        assert isinstance(report, QualityReport)
        assert 0.0 <= report.overall_score <= 1.0

    def test_very_short_output(self):
        analyzer = QualityAnalyzer()
        report = analyzer.analyze("Yes.")
        assert isinstance(report, QualityReport)

    def test_long_output(self):
        analyzer = QualityAnalyzer()
        text = " ".join([f"This is sentence number {i}." for i in range(100)])
        report = analyzer.analyze(text)
        assert isinstance(report, QualityReport)

    def test_to_dict_round_trip(self):
        analyzer = QualityAnalyzer()
        report = analyzer.analyze("A comprehensive and well-structured technical document.")
        d = report.to_dict()
        assert "scores" in d
        assert "overall_score" in d
