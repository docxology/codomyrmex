# Eval Harness — MCP Tool Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `eval_harness` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The eval harness module provides LLM evaluation capabilities, allowing agents to
run evaluation tasks and score predictions against targets using exact match or F1 metrics.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `eval_harness` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `eval_harness_run`

**Description**: Run evaluation tasks against an identity model and return metrics.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tasks` | `list[dict]` | No | Default QA tasks | List of task dicts, each with `name` and `examples` (list of `{"input": str, "target": str}`). Defaults to simple identity and case tests. |
| `metric` | `str` | No | `"exact_match"` | Metric to use: `"exact_match"` or `"f1"` |

**Returns**: `dict` — Dictionary with `status`, `num_tasks`, `mean_score`, and per-task `results`.

**Example**:
```python
from codomyrmex.eval_harness.mcp_tools import eval_harness_run

result = eval_harness_run(
    tasks=[{
        "name": "math_test",
        "examples": [
            {"input": "2+2", "target": "4"},
            {"input": "3*3", "target": "9"}
        ]
    }],
    metric="exact_match"
)
```

**Notes**: Uses an identity model by default (returns input as output). Override tasks to evaluate custom input/target pairs. Each task can optionally specify its own `metric` key.

---

### `eval_harness_score`

**Description**: Score predictions against targets using the specified metric.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `predictions` | `list[str]` | No | `["hello world", "foo bar"]` | List of predicted strings |
| `targets` | `list[str]` | No | `["hello world", "foo baz"]` | List of target/gold strings |
| `metric` | `str` | No | `"exact_match"` | `"exact_match"` or `"f1"` |

**Returns**: `dict` — Dictionary with `score` (float), `metric` (str), `num_examples` (int), and `status`.

**Example**:
```python
from codomyrmex.eval_harness.mcp_tools import eval_harness_score

result = eval_harness_score(
    predictions=["the cat sat", "on the mat"],
    targets=["the cat sat", "on a mat"],
    metric="f1"
)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: VERIFY (model evaluation), OBSERVE (benchmark scoring)
- **Dependencies**: `eval_harness.harness.EvalHarness`, `eval_harness.harness.EvalTask`, `eval_harness.harness.ExactMatchMetric`, `eval_harness.harness.F1Metric`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
