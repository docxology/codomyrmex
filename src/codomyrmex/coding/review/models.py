from typing import Any, Optional

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger




























































"""
"""Core functionality module

This module provides models functionality including:
- 0 functions: 
- 15 classes: AnalysisType, SeverityLevel, Language...

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
Review Models

Data classes and enums for code review operations.
"""




class AnalysisType(Enum):
    """Types of static analysis."""

    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    PYSCN = "pyscn"  # Advanced pyscn analysis


class SeverityLevel(Enum):
    """Severity levels for analysis results."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Language(Enum):
    """Supported programming languages."""

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
    """Result of a static analysis operation."""

    file_path: str
    line_number: int
    column_number: int
    severity: SeverityLevel
    message: str
    rule_id: str
    category: str
    suggestion: Optional[str] = None
    context: Optional[str] = None
    fix_available: bool = False
    confidence: float = 1.0


@dataclass
class AnalysisSummary:
    """Summary of analysis results for a file or project."""

    total_issues: int
    by_severity: dict[SeverityLevel, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)
    by_rule: dict[str, int] = field(default_factory=dict)
    files_analyzed: int = 0
    analysis_time: float = 0.0
    language: Optional[Language] = None
    pyscn_metrics: Optional[dict[str, Any]] = None


@dataclass
class CodeMetrics:
    """Code quality metrics."""

    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    technical_debt: float
    code_duplication: float
    test_coverage: Optional[float] = None
    documentation_coverage: Optional[float] = None


@dataclass
class ComplexityReductionSuggestion:
    """Suggestion for reducing function complexity."""

    function_name: str
    file_path: str
    current_complexity: int
    suggested_refactoring: str
    estimated_effort: str  # "low", "medium", "high"
    benefits: list[str]
    code_example: Optional[str] = None


@dataclass
class DeadCodeFinding:
    """Enhanced dead code finding with suggestions."""

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
    """Architecture compliance violation."""

    file_path: str
    violation_type: str
    description: str
    severity: str
    suggestion: str
    affected_modules: list[str] = field(default_factory=list)


@dataclass
class QualityDashboard:
    """Comprehensive code quality dashboard."""

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
    trend_direction: Optional[str] = None
    trend_percentage: Optional[float] = None


@dataclass
class QualityGateResult:
    """Result of quality gate check."""

    passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    failures: list[dict[str, Any]] = field(default_factory=list)


class CodeReviewError(CodomyrmexError):
    """Base exception for code review operations."""
    pass


class PyscnError(CodeReviewError):
    """Error in pyscn analysis."""
    pass


class ToolNotFoundError(CodeReviewError):
    """Required analysis tool not found."""
    pass


class ConfigurationError(CodeReviewError):
    """Invalid configuration provided."""
    pass

