"""
Accessibility Module

WCAG compliance checking and accessibility utilities.
"""

__version__ = "0.1.0"

from .models import (
    AccessibilityIssue,
    AccessibilityReport,
    IssueType,
    WCAGLevel,
    WCAGRule,
)
from .checker import A11yChecker
from .reporters import AccessibilityReporter
from .utils import calculate_contrast_ratio, check_heading_hierarchy

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
]
