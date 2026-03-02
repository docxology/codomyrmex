# Codomyrmex Agents — src/codomyrmex/model_ops/fine_tuning

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Fine-tuning orchestration sub-module for triggering and tracking LLM fine-tuning jobs on remote providers. Wraps the concept of a fine-tuning job with model selection, dataset association, provider routing, and status tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `fine_tuning.py` | `FineTuningJob` | Represents a fine-tuning job with `base_model`, `dataset`, `provider`, `job_id`, and `status` tracking |

## Operating Contracts

- `FineTuningJob.__init__` requires a `base_model` name, a `Dataset` instance, and an optional `provider` string (defaults to `"openai"`).
- `FineTuningJob.run()` triggers the job and sets `status` to `"running"`, returning the `job_id`.
- `FineTuningJob.refresh_status()` polls the provider for current status and updates `self.status`.
- The `Dataset` import references the sibling `datasets` sub-module (via relative import `.datasets`).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `model_ops.datasets.Dataset` (via relative import from `.datasets`)
- **Used by**: Higher-level training orchestration workflows

## Navigation

- **Parent**: [model_ops](../README.md)
- **Root**: [Root](../../../../README.md)
