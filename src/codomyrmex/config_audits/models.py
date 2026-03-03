from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Severity(Enum):
    """Audit issue severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditIssue:
    """A single issue found during an audit."""

    rule_id: str
    message: str
    severity: Severity
    file_path: str | None = None
    location: str | None = None  # e.g., line number or key path
    recommendation: str | None = None


@dataclass
class AuditResult:
    """The result of a configuration audit."""

    audit_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    issues: list[AuditIssue] = field(default_factory=list)
    success: bool = True
    summary: str = ""

    @property
    def is_compliant(self) -> bool:
        """Check if the audit is compliant (no high or critical issues)."""
        return not any(
            issue.severity in (Severity.HIGH, Severity.CRITICAL)
            for issue in self.issues
        )


@dataclass
class AuditRule:
    """A rule to be applied during an audit."""

    rule_id: str
    description: str
    severity: Severity
    check_func: Callable[[Any, str | None], list[AuditIssue]]
