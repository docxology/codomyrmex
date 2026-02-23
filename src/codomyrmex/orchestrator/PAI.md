# Personal AI Infrastructure — Orchestrator Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Orchestrator module provides DAG-based workflow construction and execution for the PAI Algorithm's PLAN phase. It defines multi-step agent workflows as directed acyclic graphs with dependency resolution, conditional branching, and parallel execution.

## PAI Capabilities

### Workflow Engine

```python
from codomyrmex.orchestrator import WorkflowEngine

engine = WorkflowEngine()

# Define DAG-based workflows
workflow = engine.create_workflow("code_review_pipeline")
workflow.add_step("scan", handler=scan_code)
workflow.add_step("review", handler=review_code, depends_on=["scan"])
workflow.add_step("fix", handler=apply_fixes, depends_on=["review"])
workflow.add_step("verify", handler=verify_fixes, depends_on=["fix"])

# Execute with dependency resolution
results = await engine.execute(workflow)
```

### Workflow Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Pipeline** | A → B → C | Sequential multi-step processing |
| **Fan-out** | A → [B, C, D] | Parallel task dispatch |
| **Fan-in** | [B, C, D] → E | Result aggregation |
| **Gate** | A → check → B or retry | Conditional execution |
| **TDD Loop** | A ↔ B | Iterative refinement |

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `WorkflowEngine` | Class | DAG workflow construction and execution |
| Workflow models | Various | Step, dependency, and result types |

## PAI Algorithm Phase Mapping

| Phase | Orchestrator Contribution |
|-------|---------------------------|
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
