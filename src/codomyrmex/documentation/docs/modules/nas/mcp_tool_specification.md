# NAS (Neural Architecture Search) — MCP Tool Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `nas` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The NAS module provides neural architecture search capabilities including
architecture sampling from a search space and random search with heuristic evaluation.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `nas` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `nas_sample_architecture`

**Description**: Sample a random architecture from the default search space.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `seed` | `int` | No | `None` | Optional random seed for reproducibility |

**Returns**: `dict` — Dictionary with `n_layers`, `d_model`, `n_heads`, `d_ff`, `dropout`, `activation`, and `total_params_estimate`.

**Example**:
```python
from codomyrmex.nas.mcp_tools import nas_sample_architecture

config = nas_sample_architecture(seed=42)
```

---

### `nas_random_search`

**Description**: Run random NAS with a size-based evaluation heuristic.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `n_trials` | `int` | No | `20` | Number of random architectures to evaluate |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` — Dictionary with `best_config` (dict with architecture hyperparameters), `best_score` (float, rounded to 4 decimals), and `total_evaluated` (int).

**Example**:
```python
from codomyrmex.nas.mcp_tools import nas_random_search

result = nas_random_search(n_trials=50, seed=42)
```

**Notes**: Uses a bell-curve heuristic centered around 10M parameters to score architectures. The best score represents how close the architecture is to the target parameter count.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: PLAN (architecture exploration), BUILD (architecture selection)
- **Dependencies**: `nas.search.ArchConfig`, `nas.search.NASSearcher`, `nas.search.NASSearchSpace`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
