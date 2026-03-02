# CI/CD Pipeline -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a full-featured CI/CD pipeline orchestration system with synchronous and asynchronous execution, dependency-aware stage scheduling, parallel job execution, config validation with cycle detection, Mermaid visualization generation, and pipeline monitoring with reporting.

## Architecture

Three-layer design: **Models** (dataclasses and enums for pipeline/stage/job), **Managers** (`PipelineManager` for local execution, `AsyncPipelineManager` for remote GitHub Actions integration via aiohttp), and **Monitor** (`PipelineMonitor` for metrics collection and report generation). Convenience functions in `functions.py` wrap common manager patterns.

## Key Classes

### `PipelineManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_pipeline` | `config_path: str` | `Pipeline` | Parse YAML/JSON config into Pipeline object |
| `run_pipeline` | `pipeline_name: str, variables: dict` | `Pipeline` | Execute pipeline synchronously (handles event loop) |
| `run_pipeline_async` | `pipeline_name: str, variables: dict` | `Pipeline` | Execute pipeline asynchronously |
| `validate_pipeline_config` | `config: dict` | `tuple[bool, list[str]]` | Validate config with detailed errors |
| `validate_stage_dependencies` | `stages: list[dict]` | `tuple[bool, list[str]]` | Detect missing deps, self-deps, cycles |
| `generate_pipeline_visualization` | `pipeline: Pipeline` | `str` | Mermaid diagram string |
| `parallel_pipeline_execution` | `stages: list[dict]` | `dict` | Execute stages respecting dependencies |
| `optimize_pipeline_schedule` | `pipeline: Pipeline` | `dict` | Analyse parallelism opportunities |
| `conditional_stage_execution` | `stage: dict, conditions: dict` | `bool` | Evaluate branch/env/custom conditions |
| `cancel_pipeline` | `pipeline_name: str` | `bool` | Cancel a running pipeline |
| `save_pipeline_config` | `pipeline: Pipeline, output_path: str` | `None` | Persist pipeline config to YAML/JSON |

### `AsyncPipelineManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `async_trigger_pipeline` | `pipeline_name, repo_owner, repo_name, workflow_id, ref, inputs` | `AsyncPipelineResult` | Trigger GitHub Actions workflow dispatch |
| `async_get_pipeline_status` | `repo_owner, repo_name, run_id, workflow_id` | `AsyncPipelineResult` | Get workflow run status |
| `async_wait_for_completion` | `repo_owner, repo_name, run_id, poll_interval, timeout` | `AsyncPipelineResult` | Poll until terminal state |
| `async_cancel_pipeline` | `repo_owner, repo_name, run_id` | `AsyncPipelineResult` | Cancel a running workflow |
| `async_get_workflow_runs` | `repo_owner, repo_name, workflow_id, status, branch` | `AsyncPipelineResult` | List workflow runs with filters |

### `PipelineMonitor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `start_monitoring` | `pipeline_name: str` | `str` | Start monitoring, returns execution_id |
| `record_stage_completion` | `execution_id, stage_name, success` | `None` | Record stage completion |
| `record_job_completion` | `execution_id, job_name, success` | `None` | Record job completion |
| `finish_monitoring` | `execution_id, status` | `PipelineMetrics` | Finish and return final metrics |
| `generate_report` | `execution_id, report_type` | `PipelineReport` | Generate and persist a report |
| `get_pipeline_health` | `pipeline_name: str` | `dict` | Get health status |
| `get_metrics_summary` | `days: int` | `dict` | Get metrics summary over time period |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`, `codomyrmex.exceptions`
- **External**: `yaml`, `aiohttp` (optional, for async remote operations), `concurrent.futures`, `asyncio`, `fnmatch`

## Constraints

- `PipelineManager` uses `ThreadPoolExecutor` (max 10 workers default) for async command execution.
- `AsyncPipelineManager` targets the GitHub Actions API by default; `base_url` and `api_token` are sourced from `CI_CD_API_URL` and `CI_CD_API_TOKEN` environment variables.
- Pipeline commands are executed with `shell=True` for variable substitution support.
- Cycle detection in `validate_stage_dependencies` uses recursive DFS and reports the first cycle found.
- `_calculate_execution_levels` uses Kahn's algorithm for topological sorting by parallelism level.
- Zero-mock: real commands are executed, `NotImplementedError` for unimplemented paths.

## Error Handling

- All errors are logged via `codomyrmex.logging_monitoring` before propagation.
- `run_pipeline_async` catches all exceptions, sets pipeline status to FAILURE, and records timestamps.
- Job failures with `allow_failure=True` are logged but do not propagate.
- `AsyncPipelineManager` methods return `AsyncPipelineResult` with `error` field rather than raising on HTTP failures.
- `PipelineMonitor.finish_monitoring` raises `CodomyrmexError` if the execution_id is unknown.
