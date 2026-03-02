"""Contextual validator for cross-field validation rules.

Provides:
- ValidationIssue: structured issue record with severity levels
- ContextualValidator: rule engine for cross-field validation
- Built-in rule factories: required_fields, mutual_exclusion, conditional_requirement,
  range_check, pattern_match, type_check
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationIssue:
    """A validation issue found during contextual validation."""

    field: str
    message: str
    severity: str = "error"  # error, warning, info
    code: str = ""  # machine-readable error code
    context: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return human-readable string."""
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


# Type alias for validation rules
ValidationRule = Callable[[dict[str, Any]], ValidationIssue | None]


class ContextualValidator:
    """Validator that supports complex cross-field validation logic.

    Allows registering custom rules, built-in rule factories, and
    batch validation with severity filtering.

    Example::

        v = ContextualValidator()
        v.add_rule(ContextualValidator.required_fields("name", "email"))
        v.add_rule(ContextualValidator.range_check("age", 0, 150))
        issues = v.validate({"name": "", "age": -1})
        # -> 2 issues: name is empty, age out of range
    """

    def __init__(self) -> None:
        self._rules: list[ValidationRule] = []
        self._rule_names: list[str] = []

    def add_rule(self, rule: ValidationRule, name: str = "") -> None:
        """Add a custom validation rule."""
        self._rules.append(rule)
        self._rule_names.append(name or f"rule_{len(self._rules)}")

    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name."""
        for i, n in enumerate(self._rule_names):
            if n == name:
                self._rules.pop(i)
                self._rule_names.pop(i)
                return True
        return False

    def validate(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate data against all registered rules."""
        issues = []
        for rule in self._rules:
            result = rule(data)
            if result is not None:
                issues.append(result)
        return issues

    def validate_many(self, records: list[dict[str, Any]]) -> dict[int, list[ValidationIssue]]:
        """Validate multiple records. Returns {index: issues} for records with issues."""
        results: dict[int, list[ValidationIssue]] = {}
        for i, record in enumerate(records):
            issues = self.validate(record)
            if issues:
                results[i] = issues
        return results

    def is_valid(self, data: dict[str, Any]) -> bool:
        """Quick check: returns True if no error-severity issues."""
        return not any(
            issue.severity == "error" for issue in self.validate(data)
        )

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    # ── Built-in Rule Factories ─────────────────────────────────────

    @staticmethod
    def required_fields(*fields: str) -> ValidationRule:
        """Rule: all listed fields must be present and non-empty."""
        def _check(data: dict[str, Any]) -> ValidationIssue | None:
            """Check the condition and return the result."""
            for f in fields:
                val = data.get(f)
                if val is None or (isinstance(val, str) and not val.strip()):
                    return ValidationIssue(
                        field=f, message=f"Required field '{f}' is missing or empty",
                        code="REQUIRED",
                    )
            return None
        return _check

    @staticmethod
    def mutual_exclusion(field_a: str, field_b: str) -> ValidationRule:
        """Rule: at most one of two fields may be set."""
        def _check(data: dict[str, Any]) -> ValidationIssue | None:
            """Check the condition and return the result."""
            if data.get(field_a) and data.get(field_b):
                return ValidationIssue(
                    field=f"{field_a}/{field_b}",
                    message=f"Fields '{field_a}' and '{field_b}' are mutually exclusive",
                    code="MUTUAL_EXCLUSION",
                )
            return None
        return _check

    @staticmethod
    def conditional_requirement(trigger_field: str, trigger_value: Any, required_field: str) -> ValidationRule:
        """Rule: if trigger_field == trigger_value then required_field must be set."""
        def _check(data: dict[str, Any]) -> ValidationIssue | None:
            """Check the condition and return the result."""
            if data.get(trigger_field) == trigger_value and not data.get(required_field):
                return ValidationIssue(
                    field=required_field,
                    message=f"'{required_field}' is required when '{trigger_field}' is '{trigger_value}'",
                    code="CONDITIONAL_REQUIRED",
                )
            return None
        return _check

    @staticmethod
    def range_check(field_name: str, min_val: float | None = None, max_val: float | None = None) -> ValidationRule:
        """Rule: numeric field must be within [min_val, max_val]."""
        def _check(data: dict[str, Any]) -> ValidationIssue | None:
            """Check the condition and return the result."""
            val = data.get(field_name)
            if val is None:
                return None
            try:
                num = float(val)
            except (ValueError, TypeError):
                return ValidationIssue(
                    field=field_name, message=f"'{field_name}' must be numeric",
                    code="TYPE_ERROR",
                )
            if min_val is not None and num < min_val:
                return ValidationIssue(
                    field=field_name, message=f"'{field_name}' must be >= {min_val}, got {num}",
                    code="RANGE_MIN",
                )
            if max_val is not None and num > max_val:
                return ValidationIssue(
                    field=field_name, message=f"'{field_name}' must be <= {max_val}, got {num}",
                    code="RANGE_MAX",
                )
            return None
        return _check

    @staticmethod
    def pattern_match(field_name: str, pattern: str, description: str = "") -> ValidationRule:
        """Rule: string field must match a regex pattern."""
        compiled = re.compile(pattern)
        def _check(data: dict[str, Any]) -> ValidationIssue | None:
            """Check the condition and return the result."""
            val = data.get(field_name)
            if val is None:
                return None
            if not compiled.match(str(val)):
                desc = description or f"must match pattern '{pattern}'"
                return ValidationIssue(
                    field=field_name, message=f"'{field_name}' {desc}",
                    code="PATTERN_MISMATCH",
                )
            return None
        return _check

    @staticmethod
    def type_check(field_name: str, expected_type: type) -> ValidationRule:
        """Rule: field value must be of the expected type."""
        def _check(data: dict[str, Any]) -> ValidationIssue | None:
            """Check the condition and return the result."""
            val = data.get(field_name)
            if val is not None and not isinstance(val, expected_type):
                return ValidationIssue(
                    field=field_name,
                    message=f"'{field_name}' expected {expected_type.__name__}, got {type(val).__name__}",
                    code="TYPE_CHECK",
                )
            return None
        return _check
