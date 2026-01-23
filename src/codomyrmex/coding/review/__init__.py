"""Code Review Submodule.

Provides comprehensive code review and static analysis capabilities including
quality assessment, security scanning, complexity analysis, dead code detection,
and clone identification. Integrates with pyscn for advanced analysis and
traditional tools like pylint, flake8, mypy, and bandit.

Public API:
    Models:
        AnalysisResult: Individual analysis finding.
        AnalysisSummary: Aggregated analysis results.
        AnalysisType: Types of analysis (quality, security, etc.).
        SeverityLevel: Issue severity levels.
        Language: Supported programming languages.
        CodeMetrics: Code quality metrics.
        QualityGateResult: Quality gate check results.

    Analysis:
        PyscnAnalyzer: Advanced pyscn-based analysis.
        CodeReviewer: Main code review orchestrator.
        analyze_file: Analyze a single file.
        analyze_project: Analyze an entire project.
        check_quality_gates: Verify quality thresholds.
        generate_report: Create HTML/JSON reports.

    Exceptions:
        CodeReviewError: Base review exception.
        PyscnError: Pyscn analysis errors.
        ToolNotFoundError: Missing analysis tools.
        ConfigurationError: Invalid configuration.

Example:
    >>> from codomyrmex.coding.review import CodeReviewer, analyze_file
    >>> reviewer = CodeReviewer(project_root="./src")
    >>> results = analyze_file("my_module.py")
    >>> for issue in results:
    ...     print(f"{issue.severity.value}: {issue.message}")
"""

# Import models
from .models import (
    AnalysisResult,
    AnalysisSummary,
    AnalysisType,
    ArchitectureViolation,
    CodeMetrics,
    CodeReviewError,
    ComplexityReductionSuggestion,
    ConfigurationError,
    DeadCodeFinding,
    Language,
    PyscnError,
    QualityDashboard,
    QualityGateResult,
    SeverityLevel,
    ToolNotFoundError,
)

# Import analyzer
from .analyzer import PyscnAnalyzer

# Import reviewer
from .reviewer import CodeReviewer, analyze_file, analyze_project, check_quality_gates, generate_report

__all__ = [
    # Models
    "AnalysisResult",
    "AnalysisSummary",
    "AnalysisType",
    "ArchitectureViolation",
    "CodeMetrics",
    "CodeReviewError",
    "ComplexityReductionSuggestion",
    "ConfigurationError",
    "DeadCodeFinding",
    "Language",
    "PyscnError",
    "QualityDashboard",
    "QualityGateResult",
    "SeverityLevel",
    "ToolNotFoundError",
    # Analyzer
    "PyscnAnalyzer",
    # Reviewer
    "CodeReviewer",
    "analyze_file",
    "analyze_project",
    "check_quality_gates",
    "generate_report",
]

