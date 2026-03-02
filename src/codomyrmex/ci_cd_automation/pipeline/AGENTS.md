# Codomyrmex Agents — src/codomyrmex/ci_cd_automation/pipeline

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides comprehensive CI/CD pipeline orchestration including pipeline creation from YAML/JSON configs, synchronous and asynchronous execution with dependency resolution, parallel job scheduling, pipeline monitoring, health checks, and reporting.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `Pipeline` | Complete pipeline definition (stages, variables, triggers, timeout) |
| `models.py` | `PipelineStage` | Stage containing multiple jobs with dependency list |
| `models.py` | `PipelineJob` | Individual job with commands, timeout, retry, allow_failure |
| `models.py` | `PipelineStatus` | Enum: PENDING, RUNNING, SUCCESS, FAILURE, CANCELLED, SKIPPED |
| `models.py` | `StageStatus` | Enum: same values as PipelineStatus |
| `models.py` | `JobStatus` | Enum: same values as PipelineStatus |
| `manager.py` | `PipelineManager` | Synchronous pipeline manager with parallel execution, config validation, Mermaid visualization, and dependency cycle detection |
| `async_manager.py` | `AsyncPipelineManager` | Async pipeline manager integrating with GitHub Actions API via aiohttp |
| `async_manager.py` | `AsyncPipelineResult` | Dataclass for async operation results |
| `async_manager.py` | `async_trigger_pipeline()` | Convenience: trigger a GitHub Actions workflow |
| `async_manager.py` | `async_get_pipeline_status()` | Convenience: get workflow run status |
| `async_manager.py` | `async_wait_for_completion()` | Convenience: poll until pipeline completes |
| `functions.py` | `create_pipeline()` | Convenience: create pipeline from config file |
| `functions.py` | `run_pipeline()` | Convenience: run a named pipeline |
| `pipeline_monitor.py` | `PipelineMonitor` | Pipeline monitoring and reporting system |
| `pipeline_monitor.py` | `PipelineMetrics` | Dataclass for pipeline performance metrics |
| `pipeline_monitor.py` | `PipelineReport` | Dataclass for comprehensive execution reports |
| `pipeline_monitor.py` | `ReportType` | Enum: EXECUTION, PERFORMANCE, QUALITY, COMPLIANCE, SUMMARY |
| `pipeline_monitor.py` | `monitor_pipeline_health()` | Convenience: get pipeline health status |
| `pipeline_monitor.py` | `generate_pipeline_reports()` | Convenience: generate multiple report types |

## Operating Contracts

- Pipeline configs must include `name` and `stages` fields; validation is enforced by `validate_pipeline_config()`.
- Stage dependencies must form a DAG; `validate_stage_dependencies()` detects cycles.
- Jobs with `allow_failure=True` do not propagate failures to the stage level.
- `AsyncPipelineManager` requires `aiohttp` and a valid API token for remote operations.
- `PipelineManager.run_pipeline()` handles event-loop detection (running loop vs none) automatically.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring`, `codomyrmex.exceptions`, `aiohttp` (optional), `yaml`
- **Used by**: `codomyrmex.ci_cd_automation` (parent), PAI EXECUTE phase agents, CLI `pipeline` commands

## Navigation

- **Parent**: [ci_cd_automation](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
