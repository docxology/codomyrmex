"""LLM output safety filtering and guardrail orchestration.

Provides content safety checks, PII detection, prompt injection
detection, and output sanitization for LLM responses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class SafetyCategory(Enum):
    """Categories of safety concern."""
    PII = "pii"
    PROMPT_INJECTION = "prompt_injection"
    HARMFUL_CONTENT = "harmful_content"
    CODE_EXECUTION = "code_execution"
    HALLUCINATION_MARKERS = "hallucination_markers"


@dataclass
class SafetyViolation:
    """A detected safety violation."""
    category: SafetyCategory
    description: str
    severity: str = "medium"  # low, medium, high, critical
    span: tuple[int, int] = (0, 0)
    suggested_action: str = "review"


@dataclass
class SafetyReport:
    """Report from a safety scan."""
    is_safe: bool
    violations: list[SafetyViolation] = field(default_factory=list)
    sanitized_text: str = ""
    original_text: str = ""

    @property
    def critical_violations(self) -> list[SafetyViolation]:
        return [v for v in self.violations if v.severity == "critical"]


class SafetyFilter:
    """LLM output safety filtering pipeline.

    Runs multiple safety checks on LLM output and can
    auto-sanitize or flag for review.
    """

    # Common PII patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

    # Prompt injection markers
    INJECTION_PATTERNS = [
        re.compile(r'(?i)ignore\s+(all\s+)?previous\s+instructions'),
        re.compile(r'(?i)you\s+are\s+now\s+'),
        re.compile(r'(?i)system\s*:\s*'),
        re.compile(r'(?i)override\s+(all\s+)?safety'),
        re.compile(r'(?i)jailbreak'),
    ]

    def __init__(self, auto_sanitize: bool = True) -> None:
        self._auto_sanitize = auto_sanitize
        self._custom_filters: list[Any] = []

    def check(self, text: str) -> SafetyReport:
        """Run all safety checks on text."""
        violations: list[SafetyViolation] = []
        violations.extend(self._check_pii(text))
        violations.extend(self._check_injection(text))
        violations.extend(self._check_code_execution(text))

        sanitized = text
        if self._auto_sanitize and violations:
            sanitized = self._sanitize(text, violations)

        return SafetyReport(
            is_safe=len(violations) == 0,
            violations=violations,
            sanitized_text=sanitized,
            original_text=text,
        )

    def _check_pii(self, text: str) -> list[SafetyViolation]:
        """Detect potential PII in text."""
        violations = []
        for match in self.EMAIL_PATTERN.finditer(text):
            violations.append(SafetyViolation(
                category=SafetyCategory.PII,
                description=f"Email address detected: {match.group()[:20]}...",
                severity="medium",
                span=match.span(),
                suggested_action="redact",
            ))
        for match in self.SSN_PATTERN.finditer(text):
            violations.append(SafetyViolation(
                category=SafetyCategory.PII,
                description="SSN-like pattern detected",
                severity="critical",
                span=match.span(),
                suggested_action="redact",
            ))
        for match in self.CREDIT_CARD_PATTERN.finditer(text):
            violations.append(SafetyViolation(
                category=SafetyCategory.PII,
                description="Credit card number detected",
                severity="critical",
                span=match.span(),
                suggested_action="redact",
            ))
        for match in self.PHONE_PATTERN.finditer(text):
            violations.append(SafetyViolation(
                category=SafetyCategory.PII,
                description="Phone number detected",
                severity="low",
                span=match.span(),
                suggested_action="review",
            ))
        return violations

    def _check_injection(self, text: str) -> list[SafetyViolation]:
        """Detect prompt injection attempts in output."""
        violations = []
        for pattern in self.INJECTION_PATTERNS:
            for match in pattern.finditer(text):
                violations.append(SafetyViolation(
                    category=SafetyCategory.PROMPT_INJECTION,
                    description=f"Potential prompt injection: '{match.group()[:50]}'",
                    severity="high",
                    span=match.span(),
                    suggested_action="block",
                ))
        return violations

    def _check_code_execution(self, text: str) -> list[SafetyViolation]:
        """Detect dangerous code execution patterns."""
        violations = []
        dangerous = [
            (r'(?i)eval\s*\(', "eval() call"),
            (r'(?i)exec\s*\(', "exec() call"),
            (r'(?i)os\.system\s*\(', "os.system() call"),
            (r'(?i)subprocess\.(run|call|Popen)\s*\(', "subprocess execution"),
            (r'(?i)__import__\s*\(', "dynamic import"),
        ]
        for pattern_str, desc in dangerous:
            pattern = re.compile(pattern_str)
            for match in pattern.finditer(text):
                violations.append(SafetyViolation(
                    category=SafetyCategory.CODE_EXECUTION,
                    description=f"Dangerous pattern: {desc}",
                    severity="high",
                    span=match.span(),
                    suggested_action="review",
                ))
        return violations

    def _sanitize(self, text: str, violations: list[SafetyViolation]) -> str:
        """Sanitize text by redacting violations."""
        result = text
        # Sort by span start descending to replace from end to avoid offset issues
        for v in sorted(violations, key=lambda x: x.span[0], reverse=True):
            if v.suggested_action == "redact" and v.span != (0, 0):
                start, end = v.span
                result = result[:start] + "[REDACTED]" + result[end:]
        return result

    def add_custom_filter(self, pattern: str, category: SafetyCategory,
                          severity: str = "medium") -> None:
        """Add a custom regex pattern as a safety filter."""
        self._custom_filters.append({
            "pattern": re.compile(pattern),
            "category": category,
            "severity": severity,
        })
