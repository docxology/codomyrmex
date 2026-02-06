"""Contextual validator for cross-field validation rules."""

from dataclasses import dataclass
from typing import Any
from collections.abc import Callable


@dataclass
class ValidationIssue:
    field: str
    message: str
    severity: str = "error"

class ContextualValidator:
    """Validator that supports complex cross-field validation logic."""

    def __init__(self):
        self._rules: list[Callable[[dict[str, Any]], ValidationIssue | None]] = []

    def add_rule(self, rule: Callable[[dict[str, Any]], ValidationIssue | None]):
        """Add a custom validation rule."""
        self._rules.append(rule)

    def validate(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate data against all registered rules."""
        issues = []
        for rule in self._rules:
            issue = rule(data)
            if issue:
                issues.append(issue)
        return issues
