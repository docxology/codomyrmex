# Task Schedulers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Placeholder submodule reserved for task scheduling algorithms within the orchestrator. Currently contains no implementation beyond the package marker. Scheduling logic is currently handled by `orchestrator.engines` (via `WorkflowDefinition.get_execution_order`) and `orchestrator.scheduler/` (the parent-level scheduler module).

## Architecture

Designed as a future extension point for pluggable scheduling strategies beyond the topological sort currently in `engines`. When implemented, schedulers would support priority-based, deadline-aware, and resource-constrained scheduling.

## Current State

- `__init__.py` exports an empty `__all__` list.
- No concrete scheduler classes or functions are implemented.

## Planned Interface

When schedulers are added, they should follow this contract:

| Class / Function | Description |
|-----------------|-------------|
| `PriorityScheduler` | Schedule tasks by configurable priority values |
| `DeadlineScheduler` | Earliest-deadline-first scheduling with preemption support |
| `ResourceAwareScheduler` | Schedule tasks based on available CPU/memory resources |
| `FairShareScheduler` | Round-robin scheduling across workflow owners for multi-tenant use |

## Dependencies

- **Internal**: `orchestrator.engines` (TaskDefinition, TaskState), `orchestrator.scheduler` (parent scheduler module)
- **External**: None currently

## Constraints

- Schedulers must respect task dependency ordering from `WorkflowDefinition.get_execution_order`.
- Scheduling decisions must be deterministic given the same input state.
- Zero-mock: real scheduling computations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Unimplemented scheduler methods must raise `NotImplementedError`.
- All errors logged before propagation.
