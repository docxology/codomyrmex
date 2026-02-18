"""Accessibility models and data types."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WCAGLevel(Enum):
    """WCAG conformance levels."""

    A = "A"
    AA = "AA"
    AAA = "AAA"


class IssueType(Enum):
    """Types of accessibility issues."""

    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"


@dataclass
class AccessibilityIssue:
    """An accessibility issue."""

    code: str
    message: str
    selector: str = ""
    issue_type: IssueType = IssueType.ERROR
    wcag_criterion: str = ""
    wcag_level: WCAGLevel = WCAGLevel.A
    suggestion: str = ""


@dataclass
class AccessibilityReport:
    """Accessibility audit report."""

    url: str = ""
    issues: list[AccessibilityIssue] = field(default_factory=list)
    passed: int = 0
    warnings: int = 0
    errors: int = 0

    @property
    def score(self) -> float:
        total = self.passed + self.errors
        if total == 0:
            return 100.0
        return (self.passed / total) * 100


class WCAGRule:
    """A WCAG accessibility rule."""

    def __init__(
        self,
        code: str,
        criterion: str,
        level: WCAGLevel,
        check_fn,
        message: str,
        suggestion: str = "",
    ):
        self.code = code
        self.criterion = criterion
        self.level = level
        self.check_fn = check_fn
        self.message = message
        self.suggestion = suggestion

    def check(self, element: dict[str, Any]) -> AccessibilityIssue | None:
        if not self.check_fn(element):
            return AccessibilityIssue(
                code=self.code,
                message=self.message,
                selector=element.get("selector", ""),
                wcag_criterion=self.criterion,
                wcag_level=self.level,
                suggestion=self.suggestion,
            )
        return None
