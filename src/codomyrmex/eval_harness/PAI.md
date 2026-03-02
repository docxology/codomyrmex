# Eval Harness -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `eval_harness_score` | Quick-check model quality on known examples |
| THINK | `eval_harness_run` | Analyze performance across multiple benchmarks |
| BUILD | `EvalHarness`, `EvalTask` (Python API) | Build custom evaluation suites |
| VERIFY | `eval_harness_run` | Validate model meets quality thresholds |
| LEARN | `eval_harness_score` | Track metric trends over training |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `eval_harness_run` | eval_harness | Run evaluation tasks and return metrics |
| `eval_harness_score` | eval_harness | Score predictions against targets |

## Agent Providers

This module does not provide agent types. It provides evaluation tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
