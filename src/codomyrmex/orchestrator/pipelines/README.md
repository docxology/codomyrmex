# pipelines

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Pipeline definitions, stages, and execution management for the orchestrator. Provides a DAG-based pipeline engine with topological stage ordering, dependency resolution, automatic retry with exponential backoff, conditional and parallel stage execution, and a fluent builder API for composing multi-stage workflows.

## Key Exports

- **`StageStatus`** -- Enum of stage execution states: PENDING, RUNNING, SUCCESS, FAILED, SKIPPED, CANCELLED
- **`PipelineStatus`** -- Enum of pipeline execution states: CREATED, RUNNING, SUCCESS, FAILED, CANCELLED
- **`StageResult`** -- Dataclass capturing a stage's execution outcome including output, error, timing, and duration
- **`PipelineResult`** -- Dataclass capturing the full pipeline run including all stage results, timing, and aggregate pass/fail counts
- **`Stage`** -- Abstract base class for pipeline stages with dependency declarations, retry count, timeout, and success/failure hooks
- **`FunctionStage`** -- Stage implementation that wraps a callable function receiving the pipeline context dict
- **`ConditionalStage`** -- Stage that evaluates a predicate function and delegates to an inner stage only when the condition is true
- **`ParallelStage`** -- Stage that executes multiple child stages concurrently using a thread pool executor
- **`Pipeline`** -- Core pipeline engine: manages stage registry, resolves topological execution order, passes dependency outputs through context, and supports fail-fast mode
- **`PipelineBuilder`** -- Fluent builder for constructing pipelines with chained `.stage()`, `.parallel()`, `.context()`, and `.build()` calls

## Directory Contents

- `__init__.py` - All pipeline classes, enums, dataclasses, and builder API
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [orchestrator](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
