# ML Pipeline — Functional Specification

**Version**: v1.3.0 | **Status**: Experimental | **Last Updated**: July 2026

## Purpose

The `ml_pipeline` module provides a lightweight interface for producing
pipeline-definition and execution-shaped receipts. Its two functions are
exported from the Python package and discovered as MCP tools. They do not
execute machine-learning workloads.

## Architecture

```
ml_pipeline/
├── __init__.py    # Explicit exports for both public functions
└── mcp_tools.py   # 2 MCP tools: ml_pipeline_create, ml_pipeline_execute
```

### Current Implementation

The module provides two stateless MCP tools that accept pipeline definitions and return structured results. Pipelines are defined as dictionaries with named steps, each step being a configuration dictionary.

#### `ml_pipeline_create`

Creates a pipeline definition from a name and list of step configurations. Returns the pipeline as a structured dictionary. Currently a pass-through (no persistence or validation).

#### `ml_pipeline_execute`

Executes a pipeline by name with provided inputs. Currently a pass-through that echoes the inputs as outputs. Future implementations will connect to actual ML frameworks.

## Data Model

### Pipeline

```python
{
    "name": str,                    # Pipeline name
    "steps": list[dict[str, Any]]   # Ordered step definitions
}
```

### Step (planned)

```python
{
    "name": str,           # Step name
    "type": str,           # Step type (e.g., "preprocess", "train", "evaluate")
    "config": dict,        # Step-specific configuration
    "depends_on": list,    # Dependencies on other steps
}
```

## Future Direction

| Capability | Status | Target |
| :--- | :--- | :--- |
| Pipeline-definition receipt | Implemented | — |
| Execution-shaped echo receipt | Implemented | — |
| Step validation | ❌ Planned | v1.3.0 |
| Pipeline persistence | ❌ Planned | v1.3.0 |
| Data loading steps | ❌ Planned | v1.3.0 |
| Training integration | ❌ Planned | v1.4.0 |
| Evaluation harness integration | ❌ Planned | v1.4.0 |

## Related Modules

| Module | Relationship |
| :--- | :--- |
| `orchestrator` | General workflow orchestration (production-ready alternative) |
| `eval_harness` | Model evaluation pipeline components |
| `model_ops` | ML model lifecycle management |

## Constraints

- **No ML execution**: `ml_pipeline_execute` returns an echo receipt
- **Stateless**: No pipeline persistence between calls
- **Zero-Mock**: Future tests must use real pipeline execution

## Navigation

- **Self**: [SPEC.md](SPEC.md) — This document
- **Parent**: [README.md](README.md) — Module overview
- **Siblings**: [AGENTS.md](AGENTS.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [PAI.md](PAI.md)
