# Model Merger -- MCP Tool Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `model_merger` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `model_merger` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `merge_models`

**Description**: Merge two model parameter sets using SLERP or linear interpolation.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `params_a` | `dict[str, list]` | Yes | -- | First model parameters (key -> list of floats) |
| `params_b` | `dict[str, list]` | Yes | -- | Second model parameters (key -> list of floats) |
| `method` | `str` | No | `"slerp"` | Merge method ('slerp' or 'linear') |
| `alpha` | `float` | No | `0.5` | Interpolation weight in [0, 1]. 0=model A, 1=model B |

**Returns**: `dict[str, Any]` -- Dictionary with merged parameter keys and shapes, or error info.

**Example**:
```python
from codomyrmex.model_merger.mcp_tools import merge_models

result = merge_models(
    params_a={"layer1": [1.0, 2.0, 3.0]},
    params_b={"layer1": [4.0, 5.0, 6.0]},
    method="linear",
    alpha=0.5,
)
```

---

### `create_model_soup`

**Description**: Create a model soup by averaging multiple model parameter sets.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `param_dicts` | `list[dict[str, list]]` | Yes | -- | List of model parameter dictionaries (key -> list of floats) |
| `weights` | `list[float]` | No | `None` | Optional weighting for each model (uniform if omitted) |

**Returns**: `dict[str, Any]` -- Dictionary with result parameter keys, shapes, and model count.

**Example**:
```python
from codomyrmex.model_merger.mcp_tools import create_model_soup

result = create_model_soup(
    param_dicts=[
        {"layer1": [1.0, 2.0]},
        {"layer1": [3.0, 4.0]},
        {"layer1": [5.0, 6.0]},
    ],
    weights=[0.5, 0.3, 0.2],
)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (model combination), VERIFY (merge validation)
- **Dependencies**: Requires `numpy` and internal `merger` module

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
