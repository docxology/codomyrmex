"""Validation manager — orchestrator for multiple validator backends.

Manages named validators, batch validation, format auto-detection,
validation profiles, and aggregate reporting.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .contextual import ContextualValidator, ValidationIssue
from .summary import ValidationSummary
from .validator import ValidationResult, Validator

logger = get_logger(__name__)


@dataclass
class ValidationRun:
    """Record of a single validation operation."""

    schema_name: str
    validator_type: str
    success: bool
    duration_ms: float
    issue_count: int


class ValidationManager:
    """Manager for validation operations with profiles, batch mode, and reporting.

    Example::

        mgr = ValidationManager()
        result = mgr.validate({"name": "test"}, {"type": "object"}, validator_type="json_schema")
        mgr.create_profile("strict", [("name_required", lambda d, s: ...)])
        batch = mgr.validate_batch([data1, data2], schema)
    """

    def __init__(self) -> None:
        self._validators: dict[str, Callable] = {}
        self._default_validator = Validator()
        self._profiles: dict[str, list[tuple[str, Callable]]] = {}
        self._history: list[ValidationRun] = []
        self._contextual = ContextualValidator()

    def register_validator(self, name: str, validator: Callable) -> None:
        """Register a custom validator function.

        Args:
            name: Validator name.
            validator: Function taking (data, schema) returning ValidationResult or bool.
        """
        self._validators[name] = validator
        logger.info("Registered custom validator: %s", name)

    def get_validator(self, name: str) -> Callable | None:
        """Get a registered validator."""
        return self._validators.get(name)

    def list_validators(self) -> list[str]:
        """List registered validator names."""
        return sorted(self._validators.keys())

    # ── Core Validation ─────────────────────────────────────────────

    def validate(self, data: Any, schema: Any, validator_type: str = "json_schema") -> ValidationResult:
        """Validate data against a schema.

        Args:
            data: Data to validate.
            schema: Validation schema.
            validator_type: Type of validator to use (or custom name).

        Returns:
            ValidationResult.
        """
        start = time.time()
        if validator_type in self._validators:
            validator_func = self._validators[validator_type]
            validator = Validator(validator_type="custom")
            result = validator._validate_custom(data, lambda d: validator_func(d, schema))
        else:
            validator = Validator(validator_type=validator_type)
            result = validator.validate(data, schema)

        self._history.append(ValidationRun(
            schema_name=str(schema.get("title", "unknown") if isinstance(schema, dict) else "unknown"),
            validator_type=validator_type,
            success=result.is_valid,
            duration_ms=(time.time() - start) * 1000,
            issue_count=len(result.errors),
        ))
        return result

    def validate_batch(
        self,
        records: list[Any],
        schema: Any,
        validator_type: str = "json_schema",
    ) -> list[ValidationResult]:
        """Validate multiple records against the same schema.

        Returns:
            List of ValidationResult for each record.
        """
        return [self.validate(record, schema, validator_type=validator_type) for record in records]

    # ── Contextual Rules ────────────────────────────────────────────

    def add_contextual_rule(self, rule: Callable, name: str = "") -> None:
        """Add a cross-field validation rule."""
        self._contextual.add_rule(rule, name=name)

    def validate_contextual(self, data: dict[str, Any]) -> ValidationSummary:
        """Run contextual rules and return a summary."""
        issues = self._contextual.validate(data)
        return ValidationSummary(issues)

    # ── Profiles ────────────────────────────────────────────────────

    def create_profile(self, name: str, rules: list[tuple[str, Callable]] | None = None) -> None:
        """Create a named validation profile with a set of rules.

        Args:
            name: Profile name.
            rules: List of (rule_name, rule_callable) pairs.
        """
        self._profiles[name] = rules or []

    def validate_with_profile(self, data: dict[str, Any], profile_name: str) -> ValidationSummary:
        """Run all rules in a named profile."""
        rules = self._profiles.get(profile_name, [])
        issues: list[ValidationIssue] = []
        for rule_name, rule_fn in rules:
            try:
                result = rule_fn(data)
                if result is not None:
                    issues.append(result if isinstance(result, ValidationIssue) else
                                  ValidationIssue(field="unknown", message=str(result)))
            except Exception as e:
                issues.append(ValidationIssue(field=rule_name, message=str(e), severity="error"))
        return ValidationSummary(issues)

    # ── Statistics ──────────────────────────────────────────────────

    @property
    def run_count(self) -> int:
        return len(self._history)

    @property
    def error_rate(self) -> float:
        """Fraction of validation runs that failed."""
        if not self._history:
            return 0.0
        return sum(1 for r in self._history if not r.success) / len(self._history)

    def summary(self) -> dict[str, Any]:
        """Return summary statistics of all validation runs."""
        if not self._history:
            return {"runs": 0, "pass_rate": 0}
        successes = sum(1 for r in self._history if r.success)
        return {
            "runs": len(self._history),
            "successes": successes,
            "failures": len(self._history) - successes,
            "pass_rate": successes / len(self._history),
            "avg_duration_ms": sum(r.duration_ms for r in self._history) / len(self._history),
            "validators_used": list({r.validator_type for r in self._history}),
        }
