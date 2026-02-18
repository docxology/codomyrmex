"""
Accessibility Module

WCAG compliance checking and accessibility utilities.
"""

__version__ = "0.1.0"

from .checker import A11yChecker
from .models import (
    AccessibilityIssue,
    AccessibilityReport,
    IssueType,
    WCAGLevel,
    WCAGRule,
)
from .reporters import AccessibilityReporter
from .utils import calculate_contrast_ratio, check_heading_hierarchy

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the accessibility module."""
    return {
        "checks": {
            "help": "List available accessibility checks and WCAG rules",
            "handler": lambda **kwargs: print(
                "Accessibility Checks:\n"
                f"  Checker: {A11yChecker.__name__}\n"
                f"  Reporter: {AccessibilityReporter.__name__}\n"
                f"  WCAG levels: {[level.name for level in WCAGLevel] if hasattr(WCAGLevel, '__iter__') else 'A, AA, AAA'}\n"
                f"  Issue types: {[it.name for it in IssueType] if hasattr(IssueType, '__iter__') else 'available'}\n"
                "  Utilities: contrast ratio, heading hierarchy"
            ),
        },
        "audit": {
            "help": "Run accessibility audit at --path (default: current directory)",
            "handler": lambda path=".", **kwargs: print(
                f"Accessibility Audit:\n"
                f"  Target path: {path}\n"
                f"  Checker: {A11yChecker.__name__} (ready)\n"
                f"  Reporter: {AccessibilityReporter.__name__} (ready)\n"
                "  Use A11yChecker().check(path) for full audit"
            ),
        },
    }


__all__ = [
    "A11yChecker",
    "AccessibilityIssue",
    "AccessibilityReport",
    "AccessibilityReporter",
    "WCAGLevel",
    "WCAGRule",
    "IssueType",
    "calculate_contrast_ratio",
    "check_heading_hierarchy",
    "cli_commands",
]
