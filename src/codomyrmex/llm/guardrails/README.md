# guardrails

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Input/output safety validation including prompt injection defense, PII detection and sanitization, content filtering, and output format validation. The `PromptInjectionDetector` checks user input against a library of regex patterns covering instruction overrides, role manipulation, system prompt extraction, delimiter exploits, and jailbreak attempts. The `PIIDetector` identifies and redacts emails, phone numbers, SSNs, credit cards, IP addresses, and dates of birth. The `Guardrail` facade combines all checks into unified `check_input()` and `check_output()` methods with configurable threat-level blocking and automatic PII sanitization.

## Key Exports

- **`ThreatLevel`** -- Enum of threat severity levels (none, low, medium, high, critical)
- **`GuardrailAction`** -- Enum of response actions (allow, warn, block, sanitize)
- **`GuardrailResult`** -- Dataclass with pass/fail status, threat level, action, detected threats list, optional sanitized content, and an `is_safe` property
- **`GuardrailConfig`** -- Configuration dataclass controlling blocking thresholds, PII sanitization toggle, max input/output lengths, and custom blocked/allowed patterns
- **`PromptInjectionDetector`** -- Regex-based detector for prompt injection attacks with 20+ built-in patterns and support for custom patterns
- **`PIIDetector`** -- Regex-based PII detector supporting 6 PII types with a `sanitize()` method that replaces matches with redaction markers (e.g., `[EMAIL]`, `[SSN]`)
- **`ContentFilter`** -- Pattern-based content safety filter for harmful/toxic content with custom pattern support
- **`OutputValidator`** -- Validates LLM output for length limits, format compliance (e.g., JSON parsing), content safety, and PII presence
- **`Guardrail`** -- Facade combining all detectors into `check_input()` (injection + content filter) and `check_output()` (validation + optional PII sanitization)
- **`check_prompt_injection()`** -- Convenience function returning True if text is free of injection patterns
- **`sanitize_pii()`** -- Convenience function that returns text with all detected PII redacted
- **`validate_llm_output()`** -- Convenience function returning True if output passes validation

## Directory Contents

- `__init__.py` - All guardrails logic: threat enums, injection detector, PII detector, content filter, output validator, unified guardrail facade
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
