# LLM Models -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Structured data models for multi-step chain-of-thought reasoning. Provides
`ReasoningStep`, `Conclusion`, and `ReasoningTrace` dataclasses with
JSON-serialization support and configurable thinking depth.

## Architecture

Pure dataclass design with no external dependencies. All types are immutable
after construction (confidence clamped in `__post_init__`). Serialization
uses `dataclasses.asdict()` with custom `from_dict` class methods for
round-trip fidelity.

## Key Classes

### `ThinkingDepth` (Enum)

| Value | Target Steps | Description |
|-------|-------------|-------------|
| `SHALLOW` | 1 | Quick pattern match |
| `NORMAL` | 3 | Standard analysis |
| `DEEP` | 5 | Exhaustive deliberation |
| `EXHAUSTIVE` | 8 | Maximum rigour |

### `ReasoningStep`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `thought` | `str` | -- | Reasoning content |
| `confidence` | `float` | `0.5` | Validity confidence (0.0--1.0, clamped) |
| `evidence` | `list[str]` | `[]` | Supporting evidence |
| `step_type` | `str` | `"reasoning"` | Category (observation, hypothesis, deduction, verification) |
| `timestamp` | `str` | auto | ISO-8601 UTC timestamp |
| `step_id` | `str` | auto | UUID hex prefix (12 chars) |

### `Conclusion`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `action` | `str` | -- | Recommended action |
| `justification` | `str` | -- | Why this action was chosen |
| `confidence` | `float` | `0.5` | Overall confidence (clamped) |
| `alternatives` | `list[str]` | `[]` | Other actions considered |
| `risks` | `list[str]` | `[]` | Identified risks or caveats |

### `ReasoningTrace`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_step` | `step: ReasoningStep` | `None` | Append step, update aggregate confidence |
| `set_conclusion` | `conclusion: Conclusion` | `None` | Set conclusion with weighted confidence |
| `to_dict` | -- | `dict` | Full serialization |
| `from_dict` | `data: dict` | `ReasoningTrace` | Deserialization |
| `to_json` / `from_json` | `str` | `str` / `ReasoningTrace` | JSON string round-trip |

## Dependencies

- **Internal**: None (standalone data models)
- **External**: stdlib only (`dataclasses`, `json`, `uuid`, `datetime`, `enum`)

## Constraints

- Confidence clamped to `[0.0, 1.0]` in all types.
- `total_confidence = mean_step_confidence * 0.7 + conclusion.confidence * 0.3`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` from `ThinkingDepth(invalid_value)`.
- `KeyError` from `from_dict()` when required fields are missing.
- All errors logged before propagation.
