# Fine-Tuning — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Orchestration layer for LLM fine-tuning jobs. Manages the lifecycle of a fine-tuning run: model selection, dataset binding, job submission to a remote provider, and status polling. Currently supports an OpenAI-style provider interface.

## Architecture

Single-class design: `FineTuningJob` encapsulates a fine-tuning run with state machine semantics (`pending` -> `running` -> `completed`). The class takes a `Dataset` from the sibling `datasets` sub-module and a provider string to route to the correct backend.

## Key Classes

### `FineTuningJob`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `base_model: str, dataset: Dataset, provider: str` | `None` | Initialize with model name, dataset, and provider (default `"openai"`) |
| `run` | — | `str` | Trigger the job; sets `status` to `"running"`, returns `job_id` |
| `refresh_status` | — | `str` | Poll provider for current status; updates and returns `self.status` |

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `base_model` | `str` | Name of the base model to fine-tune |
| `dataset` | `Dataset` | Training dataset bound to this job |
| `provider` | `str` | Provider identifier (e.g., `"openai"`) |
| `job_id` | `str or None` | Provider-assigned job ID after `run()` |
| `status` | `str` | Current job status: `"pending"`, `"running"`, or `"completed"` |

## Dependencies

- **Internal**: `model_ops.datasets.Dataset` (relative import from `.datasets`)
- **External**: Standard library only (`logging`)

## Constraints

- `run()` and `refresh_status()` currently use placeholder logic; real provider SDK integration is pending.
- Job status follows a linear state machine: `pending` -> `running` -> `completed`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All operations logged via `logger.info` before execution.
- All errors logged before propagation.
