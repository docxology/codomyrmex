"""Review Models for Code Analysis.

Data classes and enums used throughout the code review system. Provides
structured representations for analysis results, metrics, quality gates,
and error types.

Example:
    >>> from codomyrmex.coding.review.models import AnalysisResult, SeverityLevel
    >>> result = AnalysisResult(
    ...     file_path="app.py",
    ...     line_number=42,
    ...     column_number=10,
    ...     severity=SeverityLevel.WARNING,
    ...     message="Unused variable 'x'",
    ...     rule_id="W0612",
    ...     category="quality"
    ... )
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AnalysisType(Enum):
    """Types of static analysis that can be performed on code.

    Defines the categories of analysis available for code review,
    from quality checks to security scanning.

    Attributes:
        QUALITY: General code quality checks.
        SECURITY: Security vulnerability scanning.
        PERFORMANCE: Performance analysis and optimization hints.
        MAINTAINABILITY: Code maintainability assessment.
        COMPLEXITY: Cyclomatic and cognitive complexity analysis.
        STYLE: Code style and formatting checks.
        DOCUMENTATION: Documentation coverage analysis.
        TESTING: Test coverage and quality analysis.
        PYSCN: Advanced pyscn-based analysis.
    """

    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    PYSCN = "pyscn"


class SeverityLevel(Enum):
    """Severity levels for analysis results.

    Indicates the importance and urgency of addressing an issue,
    from informational to critical.

    Attributes:
        INFO: Informational finding, no action required.
        WARNING: Potential issue that should be reviewed.
        ERROR: Definite issue that should be fixed.
        CRITICAL: Severe issue requiring immediate attention.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Language(Enum):
    """Supported programming languages for analysis.

    Defines the programming languages that can be analyzed
    by the code review system.

    Attributes:
        PYTHON: Python language (.py files).
        JAVASCRIPT: JavaScript language (.js files).
        TYPESCRIPT: TypeScript language (.ts, .tsx files).
        JAVA: Java language (.java files).
        CPP: C++ language (.cpp, .cc, .cxx files).
        CSHARP: C# language (.cs files).
        GO: Go language (.go files).
        RUST: Rust language (.rs files).
        PHP: PHP language (.php files).
        RUBY: Ruby language (.rb files).
    """

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"


@dataclass
class AnalysisResult:
    """Result of a static analysis operation.

    Represents a single finding from code analysis, including its
    location, severity, and optional suggestions for fixing.

    Attributes:
        file_path: Path to the file containing the issue.
        line_number: Line number where the issue was found.
        column_number: Column number for precise location.
        severity: The severity level of the issue.
        message: Human-readable description of the issue.
        rule_id: Identifier for the rule that triggered this finding.
        category: Category of the analysis (e.g., "quality", "security").
        suggestion: Optional suggestion for fixing the issue.
        context: Optional code context around the issue.
        fix_available: Whether an automatic fix is available.
        confidence: Confidence score (0.0-1.0) for the finding.
    """

    file_path: str
    line_number: int
    column_number: int
    severity: SeverityLevel
    message: str
    rule_id: str
    category: str
    suggestion: str | None = None
    context: str | None = None
    fix_available: bool = False
    confidence: float = 1.0


@dataclass
class AnalysisSummary:
    """Summary of analysis results for a file or project.

    Aggregates analysis findings with breakdowns by severity,
    category, and rule for easy reporting and tracking.

    Attributes:
        total_issues: Total number of issues found.
        by_severity: Issue counts grouped by severity level.
        by_category: Issue counts grouped by category.
        by_rule: Issue counts grouped by rule ID.
        files_analyzed: Number of files that were analyzed.
        analysis_time: Total time taken for analysis in seconds.
        language: Primary language of the analyzed code.
        pyscn_metrics: Optional metrics from pyscn analysis.
    """

    total_issues: int
    by_severity: dict[SeverityLevel, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    files_analyzed: int = 0
    analysis_time: float = 0.0
    language: Language | None = None
    pyscn_metrics: dict[str, Any] | None = None


@dataclass
class CodeMetrics:
    """Code quality metrics for a codebase.

    Contains quantitative measurements of code quality including
    complexity, maintainability, and coverage metrics.

    Attributes:
        lines_of_code: Total lines of code (excluding blanks/comments).
        cyclomatic_complexity: McCabe cyclomatic complexity score.
        maintainability_index: Maintainability index (0-100 scale).
        technical_debt: Estimated technical debt in hours.
        code_duplication: Percentage of duplicated code.
        test_coverage: Optional test coverage percentage.
        documentation_coverage: Optional documentation coverage percentage.
    """

    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    technical_debt: float
    code_duplication: float
    test_coverage: float | None = None
    documentation_coverage: float | None = None


@dataclass
class ComplexityReductionSuggestion:
    """Suggestion for reducing function complexity.

    Provides actionable recommendations for refactoring complex
    functions to improve maintainability.

    Attributes:
        function_name: Name of the complex function.
        file_path: Path to the file containing the function.
        current_complexity: Current cyclomatic complexity score.
        suggested_refactoring: Description of suggested refactoring.
        estimated_effort: Effort estimate ("low", "medium", "high").
        benefits: List of benefits from the refactoring.
        code_example: Optional example of the refactored code.
    """

    function_name: str
    file_path: str
    current_complexity: int
    suggested_refactoring: str
    estimated_effort: str  # "low", "medium", "high"
    benefits: list[str]
    code_example: str | None = None


@dataclass
class DeadCodeFinding:
    """Enhanced dead code finding with suggestions.

    Represents detected dead or unreachable code with context
    and recommendations for removal.

    Attributes:
        file_path: Path to the file containing dead code.
        line_number: Starting line number of the dead code.
        code_snippet: The dead code snippet.
        reason: Why this code is considered dead.
        severity: Severity level of the finding.
        suggestion: Recommendation for handling the dead code.
        fix_available: Whether automatic removal is available.
        estimated_savings: Estimated benefit from removal.
    """

    file_path: str
    line_number: int
    code_snippet: str
    reason: str
    severity: str
    suggestion: str
    fix_available: bool = False
    estimated_savings: str = ""


@dataclass
class ArchitectureViolation:
    """Architecture compliance violation.

    Represents a deviation from defined architecture rules or
    best practices in module organization.

    Attributes:
        file_path: Path to the violating file.
        violation_type: Type of architecture violation.
        description: Detailed description of the violation.
        severity: Severity level of the violation.
        suggestion: Recommendation for fixing the violation.
        affected_modules: List of modules affected by this violation.
    """

    file_path: str
    violation_type: str
    description: str
    severity: str
    suggestion: str
    affected_modules: list[str] = field(default_factory=list)


@dataclass
class QualityDashboard:
    """Comprehensive code quality dashboard.

    Aggregates all quality metrics, scores, and recommendations
    into a single dashboard view for project health assessment.

    Attributes:
        overall_score: Overall quality score (0-100).
        grade: Letter grade (A, B, C, D, F).
        analysis_timestamp: ISO timestamp of the analysis.
        total_files: Number of files in the project.
        total_functions: Number of functions analyzed.
        total_lines: Total lines of code.
        complexity_score: Complexity category score.
        maintainability_score: Maintainability category score.
        testability_score: Testability category score.
        reliability_score: Reliability category score.
        security_score: Security category score.
        performance_score: Performance category score.
        complexity_metrics: Detailed complexity metrics.
        dead_code_metrics: Detailed dead code metrics.
        duplication_metrics: Detailed duplication metrics.
        coupling_metrics: Detailed coupling metrics.
        architecture_metrics: Detailed architecture metrics.
        top_complexity_issues: Top complexity issues to address.
        top_dead_code_issues: Top dead code issues to address.
        top_duplication_issues: Top duplication issues to address.
        priority_actions: High-priority recommended actions.
        quick_wins: Low-effort improvements with high impact.
        long_term_improvements: Strategic long-term improvements.
        trend_direction: Optional trend direction ("improving", "declining").
        trend_percentage: Optional trend change percentage.
    """

    overall_score: float
    grade: str
    analysis_timestamp: str
    total_files: int
    total_functions: int
    total_lines: int

    # Category scores
    complexity_score: float
    maintainability_score: float
    testability_score: float
    reliability_score: float
    security_score: float
    performance_score: float

    # Detailed metrics
    complexity_metrics: dict[str, Any]
    dead_code_metrics: dict[str, Any]
    duplication_metrics: dict[str, Any]
    coupling_metrics: dict[str, Any]
    architecture_metrics: dict[str, Any]

    # Top issues
    top_complexity_issues: list[dict[str, Any]]
    top_dead_code_issues: list[dict[str, Any]]
    top_duplication_issues: list[dict[str, Any]]

    # Recommendations
    priority_actions: list[dict[str, Any]]
    quick_wins: list[dict[str, Any]]
    long_term_improvements: list[dict[str, Any]]

    # Trends (if historical data available)
    trend_direction: str | None = None
    trend_percentage: float | None = None


@dataclass
class QualityGateResult:
    """Result of quality gate check.

    Indicates whether code passes defined quality thresholds
    with details on passed and failed checks.

    Attributes:
        passed: Whether all quality gates passed.
        total_checks: Total number of quality checks performed.
        passed_checks: Number of checks that passed.
        failed_checks: Number of checks that failed.
        failures: List of failure details with check names and values.
    """

    passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    failures: list[dict[str, Any]] = field(default_factory=list)


class CodeReviewError(CodomyrmexError):
    """Base exception for code review operations.

    Parent class for all code review-related exceptions.
    """
    pass


class PyscnError(CodeReviewError):
    """Error in pyscn analysis.

    Raised when pyscn analysis fails or produces invalid results.
    """
    pass


class ToolNotFoundError(CodeReviewError):
    """Required analysis tool not found.

    Raised when a required external tool (e.g., pylint, pyscn)
    is not installed or not available in PATH.
    """
    pass


class ConfigurationError(CodeReviewError):
    """Invalid configuration provided.

    Raised when analysis configuration is invalid or incomplete.
    """
    pass

