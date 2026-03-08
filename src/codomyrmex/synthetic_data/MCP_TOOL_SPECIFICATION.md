# Synthetic Data — MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `synthetic_data` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The synthetic data module generates structured data, classification datasets,
and preference pairs for machine learning workflows including RLHF/DPO training.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `synthetic_data` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `synth_generate_structured`

**Description**: Generate structured synthetic data from a schema definition.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fields` | `dict[str, dict[str, Any]]` | Yes | -- | Schema fields mapping name to type spec. Example: `{"age": {"type": "int", "min": 18, "max": 65}}` |
| `n_samples` | `int` | No | `100` | Number of records to generate |
| `seed` | `int` | No | `None` | Random seed for reproducibility |

**Returns**: `dict` — Dictionary with `status`, `n_samples`, `records` (first 20 records), and `truncated` (bool indicating if output was truncated).

**Example**:
```python
from codomyrmex.synthetic_data.mcp_tools import synth_generate_structured

result = synth_generate_structured(
    fields={"age": {"type": "int", "min": 18, "max": 65}, "name": {"type": "str"}},
    n_samples=50,
    seed=42
)
```

**Notes**: Returns at most 20 records in the response to avoid large payloads. The `truncated` field indicates if more records were generated than returned.

---

### `synth_generate_classification`

**Description**: Generate synthetic classification data with configurable class balance.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `n_samples` | `int` | No | `100` | Total number of samples |
| `n_classes` | `int` | No | `2` | Number of target classes |
| `n_features` | `int` | No | `10` | Feature vector dimensionality |
| `class_balance` | `str` | No | `"balanced"` | `"balanced"` or `"imbalanced"` |
| `seed` | `int` | No | `None` | Random seed |

**Returns**: `dict` — Dictionary with `status`, `n_samples`, `n_features`, `n_classes`, `class_distribution`, `features_preview` (first 5 rows), and `labels_preview` (first 20 labels).

**Example**:
```python
from codomyrmex.synthetic_data.mcp_tools import synth_generate_classification

result = synth_generate_classification(
    n_samples=200, n_classes=3, n_features=5, class_balance="imbalanced"
)
```

---

### `synth_generate_preference_pairs`

**Description**: Generate preference pairs for RLHF/DPO training.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `n_pairs` | `int` | No | `100` | Number of preference pairs |
| `seed` | `int` | No | `None` | Random seed |

**Returns**: `dict` — Dictionary with `status`, `n_pairs`, `pairs_preview` (first 5 pairs), and `truncated` (bool).

**Example**:
```python
from codomyrmex.synthetic_data.mcp_tools import synth_generate_preference_pairs

result = synth_generate_preference_pairs(n_pairs=50, seed=42)
```

**Notes**: Returns at most 5 pairs in the preview. Useful for generating RLHF/DPO training data without real human annotations.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: BUILD (generate training data), EXECUTE (produce datasets for ML pipelines)
- **Dependencies**: `synthetic_data.generator.DataSchema`, `synthetic_data.generator.SyntheticDataGenerator`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
