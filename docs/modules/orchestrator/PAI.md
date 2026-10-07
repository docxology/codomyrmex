# Personal AI Infrastructure — Orchestrator Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Orchestrator module provides DAG-based workflow construction and execution for the PAI Algorithm's PLAN phase. It defines multi-step agent workflows as directed acyclic graphs with dependency resolution, conditional branching, and parallel execution.

## PAI Capabilities

### Workflow Engine

```python
from codomyrmex.orchestrator import Workflow

# Define DAG-based workflows
workflow = Workflow("code_review_pipeline")
workflow.add_task("scan", scan_code)
workflow.add_task("review", review_code, dependencies=["scan"])
workflow.add_task("fix", apply_fixes, dependencies=["review"])
workflow.add_task("verify", verify_fixes, dependencies=["fix"])

# Execute with dependency resolution
results = await workflow.run()
```

### Workflow Patterns

| Pattern | Description | Use Case |
| --- | --- | --- |
| **Pipeline** | A → B → C | Sequential multi-step processing |
| **Fan-out** | A → [B, C, D] | Parallel task dispatch |
| **Fan-in** | [B, C, D] → E | Result aggregation |
| **Gate** | A → check → B or retry | Conditional execution |
| **TDD Loop** | A ↔ B | Iterative refinement |

## Key Exports

| Export | Type | Purpose |
| --- | --- | --- |
| `Workflow` | Class | DAG workflow construction (`add_task`) and execution (`run`) |
| Workflow models | Various | Step, dependency, and result types |

## PAI Algorithm Phase Mapping

| Phase | Orchestrator Contribution |
| --- | --- |
| **PLAN** | Construct DAG workflows from task requirements |
| **EXECUTE** | Execute workflows with dependency resolution and parallelism |
| **VERIFY** | Validate workflow completion and step outcomes |

## MCP Integration

DAG analysis tool available for inspecting workflow structure and dependencies.

## Architecture Role

**Service Layer** — Central workflow engine consuming `events/` (triggers), `concurrency/` (parallel execution), `agents/` (task dispatch). Consumed by PAI Algorithm's PLAN phase.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
