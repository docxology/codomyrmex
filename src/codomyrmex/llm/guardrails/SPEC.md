# Technical Specification - Guardrails

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.llm.guardrails`  
**Last Updated**: 2026-01-29

## 1. Purpose

Input/output safety validation including prompt injection defense

## 2. Architecture

### 2.1 Components

```
guardrails/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `llm`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.llm.guardrails
from codomyrmex.llm.guardrails import (
    ThreatLevel,               # Enum: NONE, LOW, MEDIUM, HIGH, CRITICAL
    GuardrailAction,           # Enum: ALLOW, WARN, BLOCK, SANITIZE
    GuardrailResult,           # Dataclass: passed + threat_level + action + threats_detected + sanitized_content
    GuardrailConfig,           # Dataclass: block thresholds, PII sanitization toggle, length limits, custom patterns
    PromptInjectionDetector,   # Regex-based detection of injection, jailbreak, and role-manipulation attempts
    PIIDetector,               # Detect and redact email, phone, SSN, credit card, IP, DOB
    ContentFilter,             # Pattern-based unsafe content blocking
    OutputValidator,           # Validate LLM output for length, format (JSON), content safety, and PII
    Guardrail,                 # Unified facade: check_input() and check_output() combining all detectors
    check_prompt_injection,    # Quick boolean check for prompt injection safety
    sanitize_pii,              # Sanitize PII and return cleaned text
    validate_llm_output,       # Quick boolean validation of LLM output
)

# Key class signatures:
class Guardrail:
    def __init__(self, config: GuardrailConfig | None = None): ...
    def check_input(self, text: str) -> GuardrailResult: ...
    def check_output(self, text: str, sanitize: bool = True, expected_format: str | None = None) -> GuardrailResult: ...

class PromptInjectionDetector:
    def __init__(self, config: GuardrailConfig | None = None): ...
    def detect(self, text: str) -> GuardrailResult: ...

class PIIDetector:
    def __init__(self, enabled_types: list[str] | None = None): ...
    def detect(self, text: str) -> GuardrailResult: ...
    def sanitize(self, text: str) -> tuple[str, list[str]]: ...

def check_prompt_injection(text: str) -> bool: ...
def sanitize_pii(text: str) -> str: ...
def validate_llm_output(output: str, expected_format: str | None = None) -> bool: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Regex-based detection over ML classification**: Prompt injection and PII detection use compiled regex patterns for deterministic, fast, zero-dependency operation at the cost of recall on novel attack patterns.
2. **Threat-level escalation by match count**: Multiple pattern matches escalate threat level (1 = MEDIUM, 2 = HIGH, 3+ = CRITICAL), and `GuardrailConfig.block_on_high_threat` controls whether HIGH/CRITICAL triggers BLOCK vs WARN.
3. **Unified facade pattern**: `Guardrail` composes `PromptInjectionDetector`, `PIIDetector`, `ContentFilter`, and `OutputValidator` behind `check_input` / `check_output` for single-call safety checks.

### 4.2 Limitations

- Regex-based injection detection has limited coverage against obfuscated or novel prompt injection techniques.
- PII patterns are US-centric (US phone format, SSN); international PII formats require custom patterns via `GuardrailConfig.custom_blocked_patterns`.
- Content safety patterns are simplified; production deployments should layer in an ML-based content classifier.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/llm/guardrails/
```

## 6. Future Considerations

- Add ML-based prompt injection classifier as an optional secondary detector
- Expand PII patterns for international formats (EU phone, IBAN, passport numbers)
- Add configurable allow-lists so known-safe patterns bypass detection
