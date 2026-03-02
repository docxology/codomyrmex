"""
Code-related shared types for Codomyrmex.

Provides types for code analysis, testing, and security findings.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CodeEntityType(Enum):
    """Type of code entity."""
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    MODULE = "module"
    PACKAGE = "package"
    IMPORT = "import"


class AnalysisSeverity(Enum):
    """Severity level for analysis findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecuritySeverity(Enum):
    """Severity level for security findings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestStatus(Enum):
    """Status of a test execution."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    XFAIL = "xfail"


@dataclass
class CodeEntity:
    """
    Represents a code entity (file, class, function, etc.).

    Used by static_analysis, pattern_matching, and coding modules.
    """
    name: str
    entity_type: CodeEntityType
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    language: str = "python"
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "entity_type": self.entity_type.value,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "language": self.language,
            "metadata": self.metadata,
        }


@dataclass
class AnalysisResult:
    """
    Result of a code analysis operation.

    Used by static_analysis, coding, and security modules.
    """
    analyzer: str
    target: str
    severity: AnalysisSeverity = AnalysisSeverity.INFO
    message: str = ""
    file_path: str = ""
    line: int = 0
    column: int = 0
    rule_id: str = ""
    suggestion: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "analyzer": self.analyzer,
            "target": self.target,
            "severity": self.severity.value,
            "message": self.message,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "rule_id": self.rule_id,
            "suggestion": self.suggestion,
            "metadata": self.metadata,
        }


@dataclass
class SecurityFinding:
    """
    A security-related finding from analysis or scanning.

    Used by security, static_analysis modules.
    """
    title: str
    severity: SecuritySeverity
    description: str = ""
    file_path: str = ""
    line: int = 0
    cwe_id: str = ""
    owasp_category: str = ""
    remediation: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "file_path": self.file_path,
            "line": self.line,
            "cwe_id": self.cwe_id,
            "owasp_category": self.owasp_category,
            "remediation": self.remediation,
            "metadata": self.metadata,
        }


@dataclass
class TestResult:
    """
    Result of a test execution.

    Used by testing, workflow_testing modules.
    """
    test_name: str
    status: TestStatus
    duration_ms: float = 0.0
    module: str = ""
    file_path: str = ""
    message: str = ""
    stdout: str = ""
    stderr: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "module": self.module,
            "file_path": self.file_path,
            "message": self.message,
            "metadata": self.metadata,
        }


__all__ = [
    "CodeEntity",
    "CodeEntityType",
    "AnalysisResult",
    "AnalysisSeverity",
    "SecurityFinding",
    "SecuritySeverity",
    "TestResult",
    "TestStatus",
]
