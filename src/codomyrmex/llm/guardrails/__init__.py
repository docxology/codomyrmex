"""
LLM Guardrails Module

Input/output safety validation including prompt injection defense,
content filtering, and output validation.
"""

__version__ = "0.1.0"

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ThreatLevel(Enum):
    """Threat severity levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GuardrailAction(Enum):
    """Actions to take when a guardrail is triggered."""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    SANITIZE = "sanitize"


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""
    passed: bool
    threat_level: ThreatLevel = ThreatLevel.NONE
    action: GuardrailAction = GuardrailAction.ALLOW
    message: str = ""
    threats_detected: list[str] = field(default_factory=list)
    sanitized_content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_safe(self) -> bool:
        """Check if content is safe to proceed."""
        return self.passed and self.action in [GuardrailAction.ALLOW, GuardrailAction.WARN]


@dataclass
class GuardrailConfig:
    """Configuration for guardrail behavior."""
    block_on_high_threat: bool = True
    block_on_medium_threat: bool = False
    sanitize_pii: bool = True
    max_input_length: int = 100000
    max_output_length: int = 500000
    custom_blocked_patterns: list[str] = field(default_factory=list)
    custom_allowed_patterns: list[str] = field(default_factory=list)


class PromptInjectionDetector:
    """Detects prompt injection attempts in user input."""

    # Common prompt injection patterns
    INJECTION_PATTERNS = [
        # Direct instruction override attempts
        r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"forget\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"override\s+(system|all)\s+(instructions?|prompts?|rules?)",

        # Role manipulation attempts
        r"you\s+are\s+now\s+(a|an|the)\s+",
        r"pretend\s+(to\s+be|you\s+are)\s+",
        r"act\s+as\s+(if\s+you\s+are|a|an)\s+",
        r"switch\s+to\s+.*\s+mode",
        r"enter\s+.*\s+mode",

        # System prompt extraction
        r"(show|reveal|display|print|output)\s+(your|the|system)\s+(prompt|instructions?)",
        r"what\s+(are|is)\s+(your|the)\s+(system\s+)?(prompt|instructions?)",
        r"repeat\s+(your|the)\s+(system\s+)?(prompt|instructions?)",

        # Delimiter exploitation
        r"```\s*(system|assistant|user)\s*\n",
        r"\[INST\]|\[/INST\]",
        r"<\|im_start\|>|<\|im_end\|>",
        r"<\|system\|>|<\|user\|>|<\|assistant\|>",

        # Jailbreak attempts
        r"DAN\s*mode|do\s+anything\s+now",
        r"developer\s+mode|god\s+mode",
        r"unlock(ed)?\s+mode",
    ]

    def __init__(self, config: GuardrailConfig | None = None):
        """Execute   Init   operations natively."""
        self.config = config or GuardrailConfig()
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS
        ]
        if self.config.custom_blocked_patterns:
            self._compiled_patterns.extend([
                re.compile(p, re.IGNORECASE)
                for p in self.config.custom_blocked_patterns
            ])

    def detect(self, text: str) -> GuardrailResult:
        """
        Detect prompt injection attempts in text.

        Args:
            text: Input text to analyze

        Returns:
            GuardrailResult with detection information
        """
        if not text:
            return GuardrailResult(passed=True)

        threats_detected = []

        for pattern in self._compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                threats_detected.append(f"Pattern matched: {pattern.pattern[:50]}...")

        if not threats_detected:
            return GuardrailResult(passed=True)

        threat_count = len(threats_detected)
        if threat_count >= 3:
            threat_level = ThreatLevel.CRITICAL
        elif threat_count >= 2:
            threat_level = ThreatLevel.HIGH
        else:
            threat_level = ThreatLevel.MEDIUM

        action = GuardrailAction.BLOCK if (
            self.config.block_on_high_threat and
            threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        ) else GuardrailAction.WARN

        return GuardrailResult(
            passed=False,
            threat_level=threat_level,
            action=action,
            message=f"Detected {threat_count} potential prompt injection pattern(s)",
            threats_detected=threats_detected,
        )


class PIIDetector:
    """Detects and optionally sanitizes Personally Identifiable Information."""

    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone_us": r"\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b",
        "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "date_of_birth": r"\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b",
    }

    REDACTION_MAP = {
        "email": "[EMAIL]",
        "phone_us": "[PHONE]",
        "ssn": "[SSN]",
        "credit_card": "[CREDIT_CARD]",
        "ip_address": "[IP_ADDRESS]",
        "date_of_birth": "[DOB]",
    }

    def __init__(self, enabled_types: list[str] | None = None):
        """
        Initialize PII detector.

        Args:
            enabled_types: List of PII types to detect. If None, detect all.
        """
        self.enabled_types = enabled_types or list(self.PII_PATTERNS.keys())
        self._compiled_patterns = {
            pii_type: re.compile(pattern, re.IGNORECASE)
            for pii_type, pattern in self.PII_PATTERNS.items()
            if pii_type in self.enabled_types
        }

    def detect(self, text: str) -> GuardrailResult:
        """
        Detect PII in text.

        Args:
            text: Input text to analyze

        Returns:
            GuardrailResult with PII detection information
        """
        if not text:
            return GuardrailResult(passed=True)

        threats_detected = []
        pii_found: dict[str, list[str]] = {}

        for pii_type, pattern in self._compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                pii_found[pii_type] = matches
                threats_detected.append(f"{pii_type}: {len(matches)} instance(s)")

        if not threats_detected:
            return GuardrailResult(passed=True)

        return GuardrailResult(
            passed=False,
            threat_level=ThreatLevel.MEDIUM,
            action=GuardrailAction.SANITIZE,
            message=f"Detected PII: {', '.join(pii_found.keys())}",
            threats_detected=threats_detected,
            metadata={"pii_types": list(pii_found.keys())},
        )

    def sanitize(self, text: str) -> tuple[str, list[str]]:
        """
        Sanitize PII from text by replacing with redaction markers.

        Args:
            text: Input text to sanitize

        Returns:
            Tuple of (sanitized text, list of redacted types)
        """
        if not text:
            return text, []

        redacted_types = []
        sanitized = text

        for pii_type, pattern in self._compiled_patterns.items():
            if pattern.search(sanitized):
                sanitized = pattern.sub(self.REDACTION_MAP[pii_type], sanitized)
                redacted_types.append(pii_type)

        return sanitized, redacted_types


class ContentFilter:
    """Filters content for safety and appropriateness."""

    # Basic toxic content patterns (simplified for demo)
    TOXIC_PATTERNS = [
        r"\b(kill|murder|attack)\s+(yourself|yourself|them|him|her)\b",
        r"\bhow\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive)\b",
        r"\b(hack|break\s+into)\s+(a\s+)?(bank|account|system)\b",
    ]

    def __init__(self, custom_patterns: list[str] | None = None):
        """Execute   Init   operations natively."""
        self.patterns = self.TOXIC_PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.patterns
        ]

    def check(self, text: str) -> GuardrailResult:
        """
        Check content for safety issues.

        Args:
            text: Content to check

        Returns:
            GuardrailResult with content safety information
        """
        if not text:
            return GuardrailResult(passed=True)

        threats_detected = []

        for pattern in self._compiled_patterns:
            if pattern.search(text):
                threats_detected.append("Unsafe content pattern detected")

        if not threats_detected:
            return GuardrailResult(passed=True)

        return GuardrailResult(
            passed=False,
            threat_level=ThreatLevel.HIGH,
            action=GuardrailAction.BLOCK,
            message="Content failed safety check",
            threats_detected=threats_detected,
        )


class OutputValidator:
    """Validates LLM output for safety and format compliance."""

    def __init__(self, config: GuardrailConfig | None = None):
        """Execute   Init   operations natively."""
        self.config = config or GuardrailConfig()
        self.pii_detector = PIIDetector()
        self.content_filter = ContentFilter()

    def validate(
        self,
        output: str,
        expected_format: str | None = None,
        max_length: int | None = None
    ) -> GuardrailResult:
        """
        Validate LLM output.

        Args:
            output: LLM output to validate
            expected_format: Expected format ("json", "code", "text", etc.)
            max_length: Maximum allowed length

        Returns:
            GuardrailResult with validation information
        """
        threats_detected = []
        max_len = max_length or self.config.max_output_length

        # Length check
        if len(output) > max_len:
            threats_detected.append(f"Output exceeds max length ({len(output)} > {max_len})")

        # Format validation
        if expected_format == "json":
            try:
                json.loads(output)
            except json.JSONDecodeError as e:
                threats_detected.append(f"Invalid JSON: {str(e)[:50]}")

        # Content safety
        content_result = self.content_filter.check(output)
        if not content_result.passed:
            threats_detected.extend(content_result.threats_detected)

        # PII check
        if self.config.sanitize_pii:
            pii_result = self.pii_detector.detect(output)
            if not pii_result.passed:
                threats_detected.extend(pii_result.threats_detected)

        if not threats_detected:
            return GuardrailResult(passed=True)

        return GuardrailResult(
            passed=False,
            threat_level=ThreatLevel.MEDIUM,
            action=GuardrailAction.WARN,
            message=f"Output validation found {len(threats_detected)} issue(s)",
            threats_detected=threats_detected,
        )


class Guardrail:
    """
    Main guardrail class combining all safety checks.

    Usage:
        guardrail = Guardrail()

        # Check input
        result = guardrail.check_input(user_message)
        if not result.is_safe:
            print(f"Blocked: {result.message}")
            return

        # Process with LLM...

        # Check output
        result = guardrail.check_output(llm_response)
        if result.action == GuardrailAction.SANITIZE:
            response = result.sanitized_content
    """

    def __init__(self, config: GuardrailConfig | None = None):
        """Execute   Init   operations natively."""
        self.config = config or GuardrailConfig()
        self.injection_detector = PromptInjectionDetector(self.config)
        self.pii_detector = PIIDetector()
        self.content_filter = ContentFilter()
        self.output_validator = OutputValidator(self.config)

    def check_input(self, text: str) -> GuardrailResult:
        """
        Run all input safety checks.

        Args:
            text: User input to check

        Returns:
            Aggregated GuardrailResult
        """
        all_threats = []
        highest_threat = ThreatLevel.NONE
        action = GuardrailAction.ALLOW

        # Length check
        if len(text) > self.config.max_input_length:
            return GuardrailResult(
                passed=False,
                threat_level=ThreatLevel.MEDIUM,
                action=GuardrailAction.BLOCK,
                message=f"Input exceeds maximum length of {self.config.max_input_length}",
            )

        # Prompt injection check
        injection_result = self.injection_detector.detect(text)
        if not injection_result.passed:
            all_threats.extend(injection_result.threats_detected)
            if injection_result.threat_level.value > highest_threat.value:
                highest_threat = injection_result.threat_level
            if injection_result.action == GuardrailAction.BLOCK:
                action = GuardrailAction.BLOCK

        # Content filter
        content_result = self.content_filter.check(text)
        if not content_result.passed:
            all_threats.extend(content_result.threats_detected)
            if content_result.threat_level.value > highest_threat.value:
                highest_threat = content_result.threat_level
            if content_result.action == GuardrailAction.BLOCK:
                action = GuardrailAction.BLOCK

        if not all_threats:
            return GuardrailResult(passed=True)

        return GuardrailResult(
            passed=action != GuardrailAction.BLOCK,
            threat_level=highest_threat,
            action=action,
            message=f"Input check found {len(all_threats)} issue(s)",
            threats_detected=all_threats,
        )

    def check_output(
        self,
        text: str,
        sanitize: bool = True,
        expected_format: str | None = None
    ) -> GuardrailResult:
        """
        Run all output safety checks.

        Args:
            text: LLM output to check
            sanitize: Whether to sanitize PII if found
            expected_format: Expected output format

        Returns:
            GuardrailResult with optional sanitized content
        """
        result = self.output_validator.validate(text, expected_format)

        if sanitize and self.config.sanitize_pii:
            sanitized, redacted_types = self.pii_detector.sanitize(text)
            if redacted_types:
                result.sanitized_content = sanitized
                result.metadata["redacted_pii_types"] = redacted_types
                if result.action == GuardrailAction.ALLOW:
                    result.action = GuardrailAction.SANITIZE

        return result


# Convenience functions
def check_prompt_injection(text: str) -> bool:
    """Quick check for prompt injection. Returns True if safe."""
    detector = PromptInjectionDetector()
    return detector.detect(text).passed


def sanitize_pii(text: str) -> str:
    """Sanitize PII from text and return cleaned version."""
    detector = PIIDetector()
    sanitized, _ = detector.sanitize(text)
    return sanitized


def validate_llm_output(output: str, expected_format: str | None = None) -> bool:
    """Quick validation of LLM output. Returns True if valid."""
    validator = OutputValidator()
    return validator.validate(output, expected_format).passed


__all__ = [
    # Enums
    "ThreatLevel",
    "GuardrailAction",
    # Data classes
    "GuardrailResult",
    "GuardrailConfig",
    # Classes
    "PromptInjectionDetector",
    "PIIDetector",
    "ContentFilter",
    "OutputValidator",
    "Guardrail",
    # Functions
    "check_prompt_injection",
    "sanitize_pii",
    "validate_llm_output",
]
