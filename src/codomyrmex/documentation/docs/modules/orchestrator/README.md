<!-- readme: generated -->

# orchestrator

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/orchestrator/`

## Overview

Script Orchestrator Module

This module provides functionality for discovering, configuring, and running
Python scripts within the Codomyrmex project.

Features:
- Script discovery and execution
- Workflow DAG execution with dependencies
- Parallel execution with resource management
- Retry logic and conditional execution
- Progress streaming and callbacks

## Submodules

| Submodule | Description |
|-----------|-------------|
| `scheduler:` | Consolidated scheduler capabilities. |

## Public Exports

`orchestrator` exports 77 public symbols via `__all__`:

`AgentOrchestrator`, `AsyncExecutionResult`, `AsyncJob`, `AsyncJobStatus`, `AsyncParallelRunner`, `AsyncScheduler`, `AsyncTaskResult`, `BatchRunner`, `CICDBridge`, `ConcurrencyError`, `CycleError`, `DependencyResolutionError`, `ExecutionResult`, `HTNPlanner`, `Method`, `Operator`, `OrchestratorBridge`, `OrchestratorTimeoutError`, `ParallelRunner`, `PipelineConfig`, `RetryPolicy`, `SchedulerMetrics`, `StageConfig`, `State` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../orchestrator/](../../../../orchestrator/)
