"""Guardrail detectors: PromptInjectionDetector, PIIDetector, ContentFilter."""

import re

from .models import GuardrailAction, GuardrailConfig, GuardrailResult, ThreatLevel


class PromptInjectionDetector:
    """Detects prompt injection attempts in user input."""

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"forget\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"override\s+(system|all)\s+(instructions?|prompts?|rules?)",
        r"you\s+are\s+now\s+(a|an|the)\s+",
        r"pretend\s+(to\s+be|you\s+are)\s+",
        r"act\s+as\s+(if\s+you\s+are|a|an)\s+",
        r"switch\s+to\s+.*\s+mode",
        r"enter\s+.*\s+mode",
        r"(show|reveal|display|print|output)\s+(your|the|system)\s+(prompt|instructions?)",
        r"what\s+(are|is)\s+(your|the)\s+(system\s+)?(prompt|instructions?)",
        r"repeat\s+(your|the)\s+(system\s+)?(prompt|instructions?)",
        r"```\s*(system|assistant|user)\s*\n",
        r"\[INST\]|\[/INST\]",
        r"<\|im_start\|>|<\|im_end\|>",
        r"<\|system\|>|<\|user\|>|<\|assistant\|>",
        r"DAN\s*mode|do\s+anything\s+now",
        r"developer\s+mode|god\s+mode",
        r"unlock(ed)?\s+mode",
    ]

    def __init__(self, config: GuardrailConfig | None = None):
        self.config = config or GuardrailConfig()
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS
        ]
        if self.config.custom_blocked_patterns:
            self._compiled_patterns.extend(
                re.compile(p, re.IGNORECASE)
                for p in self.config.custom_blocked_patterns
            )

    def detect(self, text: str) -> GuardrailResult:
        """Detect prompt injection attempts in text."""
        if not text:
            return GuardrailResult(passed=True)

        threats_detected = [
            f"Pattern matched: {pattern.pattern[:50]}..."
            for pattern in self._compiled_patterns
            if pattern.findall(text)
        ]

        if not threats_detected:
            return GuardrailResult(passed=True)

        threat_count = len(threats_detected)
        if threat_count >= 3:
            threat_level = ThreatLevel.CRITICAL
        elif threat_count >= 2:
            threat_level = ThreatLevel.HIGH
        else:
            threat_level = ThreatLevel.MEDIUM

        action = (
            GuardrailAction.BLOCK
            if self.config.block_on_high_threat
            and threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
            else GuardrailAction.WARN
        )

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
        self.enabled_types = enabled_types or list(self.PII_PATTERNS.keys())
        self._compiled_patterns = {
            pii_type: re.compile(pattern, re.IGNORECASE)
            for pii_type, pattern in self.PII_PATTERNS.items()
            if pii_type in self.enabled_types
        }

    def detect(self, text: str) -> GuardrailResult:
        """Detect PII in text."""
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
        """Sanitize PII from text by replacing with redaction markers."""
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

    TOXIC_PATTERNS = [
        r"\b(kill|murder|attack)\s+(yourself|yourself|them|him|her)\b",
        r"\bhow\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive)\b",
        r"\b(hack|break\s+into)\s+(a\s+)?(bank|account|system)\b",
    ]

    def __init__(self, custom_patterns: list[str] | None = None):
        self.patterns = self.TOXIC_PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.patterns]

    def check(self, text: str) -> GuardrailResult:
        """Check content for safety issues."""
        if not text:
            return GuardrailResult(passed=True)

        threats_detected = [
            "Unsafe content pattern detected"
            for pattern in self._compiled_patterns
            if pattern.search(text)
        ]

        if not threats_detected:
            return GuardrailResult(passed=True)

        return GuardrailResult(
            passed=False,
            threat_level=ThreatLevel.HIGH,
            action=GuardrailAction.BLOCK,
            message="Content failed safety check",
            threats_detected=threats_detected,
        )
