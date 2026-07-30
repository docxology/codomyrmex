# Ml Pipeline — Functional Specification

**Module**: `codomyrmex.ml_pipeline`  
**Version**: v1.3.0
**Status**: Experimental

## 1. Overview

Two stateless, MCP-backed Python functions produce structured pipeline
definition and execution-shaped receipts. No pipeline state is persisted and
no machine-learning workload is executed.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `ml_pipeline_create` | Python export and MCP tool | Echoes a named step definition |
| `ml_pipeline_execute` | Python export and MCP tool | Echoes named inputs as an execution-shaped receipt |

### Source Files

- `mcp_tools.py`

## 3. Dependencies

See `src/codomyrmex/ml_pipeline/__init__.py` for import dependencies.

## 4. Public API

The package exports `ml_pipeline_create` and `ml_pipeline_execute`. The
canonical signatures and result schemas are in the
[source API specification](../../../src/codomyrmex/ml_pipeline/API_SPECIFICATION.md).

## 5. Testing

```bash
uv run --locked pytest tests/unit/ml_pipeline -v
```

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../README.md)
