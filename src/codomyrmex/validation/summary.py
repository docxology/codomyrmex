"""Validation summary for batch error reporting."""

from typing import List, Dict, Any
from .contextual import ValidationIssue

class ValidationSummary:
    """Summarizes multiple validation issues for reporting."""
    
    def __init__(self, issues: List[ValidationIssue]):
        self.issues = issues

    @property
    def is_valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    @property
    def error_count(self) -> int:
        return len([i for i in self.issues if i.severity == "error"])

    @property
    def warning_count(self) -> int:
        return len([i for i in self.issues if i.severity == "warning"])

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to a dictionary."""
        return {
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [
                {"field": i.field, "message": i.message, "severity": i.severity}
                for i in self.issues
            ]
        }
