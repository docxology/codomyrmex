# Fine-Tuning — Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: October 2026

## Overview

Orchestration layer for LLM fine-tuning jobs: dataset binding, job submission to a remote provider, status polling and cancellation. The only implemented provider is OpenAI (official `openai` SDK); every other provider raises `NotImplementedError`. No job IDs or statuses are ever invented locally.

## Architecture

Single-class design: `FineTuningJob` wraps one provider job. It starts as `"pending"` (not submitted). `run()` uploads the training JSONL (`files.create(purpose="fine-tune")`) and creates the job (`fine_tuning.jobs.create`); afterwards `status` holds the provider's own status string (`validating_files`, `queued`, `running`, `succeeded`, `failed`, `cancelled`). The dataset is either the file-backed `Dataset` dataclass in this module or any in-memory dataset implementing `JsonlExportable` (`data` + `to_jsonl()`), such as `codomyrmex.model_ops.Dataset`. `codomyrmex.model_ops.FineTuningJob` is this class.

## Key Classes

### `FineTuningJob`

| Method | Parameters | Returns | Description |
| --- | --- | --- | --- |
| `__init__` | `base_model: str, dataset: Dataset \| JsonlExportable, provider: str = "openai", *, hyperparameters: dict \| None, suffix: str \| None, api_key: str \| None` | `None` | Bind model, data and provider. `api_key` defaults to `OPENAI_API_KEY`, read on first provider call |
| `run` | — | `str` | Validate the dataset locally, upload it, create the provider job; returns the provider job ID |
| `refresh_status` | — | `str` | Retrieve the job from the provider and update `status`; an unsubmitted job stays `"pending"` without a provider call |
| `cancel` | — | `str` | Cancel the submitted job on the provider; returns the reported status |
| `to_dict` | — | `dict` | Current provider-reported state |

### Instance Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `base_model` | `str` | Name of the base model to fine-tune |
| `dataset` | `Dataset \| JsonlExportable` | Training dataset bound to this job |
| `provider` | `str` | Provider identifier (`"openai"`) |
| `job_id` | `str or None` | Provider-assigned job ID after `run()` |
| `status` | `str` | `"pending"` before submission, then the provider's status |
| `training_file_id` | `str or None` | Provider file ID of the uploaded training data |
| `fine_tuned_model` | `str or None` | Resulting model name once the provider reports it |
| `error` | `str or None` | Provider error message for a failed job |

## Dependencies

- **Internal**: `codomyrmex.exceptions` (`DependencyError`, `EnvironmentError`), `logging_monitoring`
- **External**: `openai` SDK, imported lazily (`uv sync --extra llm_providers`)

## Constraints

- Only `provider="openai"` is implemented; others raise `NotImplementedError` from `run()`, `refresh_status()` and `cancel()` on a submitted job.
- `run()` refuses to submit the same job twice (`RuntimeError`).
- Submitting a job is a billed provider call; tests never submit one.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Local validation errors: `FileNotFoundError` (missing training file), `ValueError` (empty dataset or non-JSONL format), `TypeError` (unsupported dataset type).
- `DependencyError` when the `openai` SDK is missing; `codomyrmex.exceptions.EnvironmentError` when no API key is available.
- Provider errors (`openai.APIError` subclasses) propagate unchanged.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
