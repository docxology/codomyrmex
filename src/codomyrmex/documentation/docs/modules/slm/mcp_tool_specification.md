# SLM (Small Language Model) — MCP Tool Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `slm` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The SLM module provides a tiny transformer-based language model for experimentation,
supporting both token generation and forward-pass logit analysis.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `slm` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `slm_generate`

**Description**: Generate tokens from a tiny language model.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt_tokens` | `list[int]` | No | `[1, 2, 3]` | List of integer token IDs for the prompt |
| `max_new_tokens` | `int` | No | `10` | Number of new tokens to generate |
| `vocab_size` | `int` | No | `100` | Vocabulary size |
| `d_model` | `int` | No | `32` | Model dimension |
| `n_heads` | `int` | No | `2` | Number of attention heads |
| `n_layers` | `int` | No | `1` | Number of transformer layers |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` — Dictionary with `prompt` (original tokens), `generated` (new tokens), `full_sequence` (concatenation), `vocab_size`, `model_params` (dict), and `status`.

**Example**:
```python
from codomyrmex.slm.mcp_tools import slm_generate

result = slm_generate(prompt_tokens=[1, 5, 10], max_new_tokens=20, vocab_size=200)
```

**Notes**: Creates a fresh model instance on each call with random weights. Useful for testing generation pipelines, not for meaningful text output.

---

### `slm_forward`

**Description**: Run a forward pass through the SLM and return logit statistics.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `batch_size` | `int` | No | `1` | Number of sequences in the batch |
| `seq_len` | `int` | No | `8` | Length of each sequence |
| `vocab_size` | `int` | No | `100` | Vocabulary size |
| `d_model` | `int` | No | `32` | Model dimension |
| `n_heads` | `int` | No | `2` | Number of attention heads |
| `n_layers` | `int` | No | `1` | Number of transformer layers |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` — Dictionary with `output_shape`, `logit_mean`, `logit_std`, `logit_min`, `logit_max`, and `status`.

**Example**:
```python
from codomyrmex.slm.mcp_tools import slm_forward

result = slm_forward(batch_size=2, seq_len=16, d_model=64, n_heads=4)
```

**Notes**: Generates random token IDs internally. Returns statistical summaries of the logit tensor rather than the full output.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: BUILD (model prototyping), VERIFY (output shape/statistics validation)
- **Dependencies**: `numpy`, `slm.model.SLM`, `slm.model.SLMConfig`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
