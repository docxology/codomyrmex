"""
Data models for the static analysis module.

Enums and dataclasses shared across the static_analyzer and tool_runners.
"""

from dataclasses import dataclass, field
from enum import Enum


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
    suggestion: str | None = None
    context: str | None = None
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
    language: Language | None = None


@dataclass
class CodeMetrics:
    """Code quality metrics."""

    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    technical_debt: float
    code_duplication: float
    test_coverage: float | None = None
    documentation_coverage: float | None = None
