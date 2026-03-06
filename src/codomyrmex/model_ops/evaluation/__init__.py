"""
Model Evaluation Module for Codomyrmex.

Provides tools for evaluating LLM model outputs including:
- Output scoring with composable scorer protocols
- Benchmark suite management for systematic evaluation
- Heuristic quality analysis across multiple dimensions

Integration:
- Uses `codomyrmex.validation.schemas` for Result/ResultStatus types where available.
- No external LLM dependencies required; all scoring is heuristic-based.

Available scorers:
- ExactMatchScorer: Binary exact string match
- ContainsScorer: Substring containment check
- LengthScorer: Output length relative to target range
- RegexScorer: Regex pattern matching
- CompositeScorer: Weighted combination of multiple scorers

Benchmark management:
- BenchmarkCase: Individual test case definition
- BenchmarkSuite: Collection runner with scoring
- BenchmarkResult: Per-case evaluation result
- SuiteResult: Aggregated suite-level results

Quality analysis:
- QualityAnalyzer: Multi-dimension heuristic quality scorer
- QualityDimension: COHERENCE, RELEVANCE, COMPLETENESS, CONCISENESS, ACCURACY
- QualityReport: Structured quality assessment report
"""

try:
    from .benchmarks import (
        BenchmarkCase,
        BenchmarkResult,
        BenchmarkSuite,
        SuiteResult,
    )
    from .quality import (
        DimensionScore,
        QualityAnalyzer,
        QualityDimension,
        QualityReport,
        analyze_quality,
    )
    from .scorers import (
        CompositeScorer,
        ContainsScorer,
        ExactMatchScorer,
        LengthScorer,
        RegexScorer,
        Scorer,
        WeightedScorer,
        create_default_scorer,
    )

    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    _import_error = str(_exc)

    def _not_available(*args, **kwargs):
        raise ImportError(f"model_evaluation module is not available: {_import_error}")

    create_default_scorer = _not_available  # type: ignore


    analyze_quality = _not_available  # type: ignore

# Metrics module (classification/regression evaluation)
from .metrics import (
    AccuracyMetric,
    AUCROCMetric,
    ConfusionMatrix,
    EvaluationResult,
    F1Metric,
    MAEMetric,
    Metric,
    ModelEvaluator,
    MSEMetric,
    PrecisionMetric,
    R2Metric,
    RecallMetric,
    RMSEMetric,
    TaskType,
    create_evaluator,
)

__all__ = [
    "AUCROCMetric",
    "AccuracyMetric",
    # Benchmarks
    "BenchmarkCase",
    "BenchmarkResult",
    "BenchmarkSuite",
    "CompositeScorer",
    "ConfusionMatrix",
    "ContainsScorer",
    "DimensionScore",
    "EvaluationResult",
    "ExactMatchScorer",
    "F1Metric",
    "LengthScorer",
    "MAEMetric",
    "MSEMetric",
    "Metric",
    "ModelEvaluator",
    "PrecisionMetric",
    "QualityAnalyzer",
    # Quality
    "QualityDimension",
    "QualityReport",
    "R2Metric",
    "RMSEMetric",
    "RecallMetric",
    "RegexScorer",
    # Scorers
    "Scorer",
    "SuiteResult",
    # Metrics
    "TaskType",
    "WeightedScorer",
    "analyze_quality",
    "create_default_scorer",
    "create_evaluator",
]

__version__ = "0.1.0"
