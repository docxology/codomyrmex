"""OutputValidator, Guardrail, and convenience functions."""

import json

from .detectors import ContentFilter, PIIDetector, PromptInjectionDetector
from .models import GuardrailAction, GuardrailConfig, GuardrailResult, ThreatLevel


class OutputValidator:
    """Validates LLM output for safety and format compliance."""

    def __init__(self, config: GuardrailConfig | None = None):
        self.config = config or GuardrailConfig()
        self.pii_detector = PIIDetector()
        self.content_filter = ContentFilter()

    def validate(
        self,
        output: str,
        expected_format: str | None = None,
        max_length: int | None = None,
    ) -> GuardrailResult:
        """Validate LLM output."""
        threats_detected = []
        max_len = max_length or self.config.max_output_length

        if len(output) > max_len:
            threats_detected.append(f"Output exceeds max length ({len(output)} > {max_len})")

        if expected_format == "json":
            try:
                json.loads(output)
            except json.JSONDecodeError as e:
                threats_detected.append(f"Invalid JSON: {str(e)[:50]}")

        content_result = self.content_filter.check(output)
        if not content_result.passed:
            threats_detected.extend(content_result.threats_detected)

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
        result = guardrail.check_input(user_message)
        if not result.is_safe:
            return
        result = guardrail.check_output(llm_response)
        if result.action == GuardrailAction.SANITIZE:
            response = result.sanitized_content
    """

    def __init__(self, config: GuardrailConfig | None = None):
        self.config = config or GuardrailConfig()
        self.injection_detector = PromptInjectionDetector(self.config)
        self.pii_detector = PIIDetector()
        self.content_filter = ContentFilter()
        self.output_validator = OutputValidator(self.config)

    def check_input(self, text: str) -> GuardrailResult:
        """Run all input safety checks."""
        if len(text) > self.config.max_input_length:
            return GuardrailResult(
                passed=False,
                threat_level=ThreatLevel.MEDIUM,
                action=GuardrailAction.BLOCK,
                message=f"Input exceeds maximum length of {self.config.max_input_length}",
            )

        all_threats = []
        highest_threat = ThreatLevel.NONE
        action = GuardrailAction.ALLOW

        injection_result = self.injection_detector.detect(text)
        if not injection_result.passed:
            all_threats.extend(injection_result.threats_detected)
            if injection_result.threat_level.value > highest_threat.value:
                highest_threat = injection_result.threat_level
            if injection_result.action == GuardrailAction.BLOCK:
                action = GuardrailAction.BLOCK

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
        self, text: str, sanitize: bool = True, expected_format: str | None = None
    ) -> GuardrailResult:
        """Run all output safety checks."""
        result = self.output_validator.validate(text, expected_format)

        if sanitize and self.config.sanitize_pii:
            sanitized, redacted_types = self.pii_detector.sanitize(text)
            if redacted_types:
                result.sanitized_content = sanitized
                result.metadata["redacted_pii_types"] = redacted_types
                if result.action == GuardrailAction.ALLOW:
                    result.action = GuardrailAction.SANITIZE

        return result


def check_prompt_injection(text: str) -> bool:
    """Quick check for prompt injection. Returns True if safe."""
    return PromptInjectionDetector().detect(text).passed


def sanitize_pii(text: str) -> str:
    """Sanitize PII from text and return cleaned version."""
    sanitized, _ = PIIDetector().sanitize(text)
    return sanitized


def validate_llm_output(output: str, expected_format: str | None = None) -> bool:
    """Quick validation of LLM output. Returns True if valid."""
    return OutputValidator().validate(output, expected_format).passed
