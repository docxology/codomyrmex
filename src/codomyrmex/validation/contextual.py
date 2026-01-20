"""Contextual validator for cross-field validation rules."""

from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    field: str
    message: str
    severity: str = "error"

class ContextualValidator:
    """Validator that supports complex cross-field validation logic."""
    
    def __init__(self):
        self._rules: List[Callable[[Dict[str, Any]], Optional[ValidationIssue]]] = []

    def add_rule(self, rule: Callable[[Dict[str, Any]], Optional[ValidationIssue]]):
        """Add a custom validation rule."""
        self._rules.append(rule)

    def validate(self, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate data against all registered rules."""
        issues = []
        for rule in self._rules:
            issue = rule(data)
            if issue:
                issues.append(issue)
        return issues
