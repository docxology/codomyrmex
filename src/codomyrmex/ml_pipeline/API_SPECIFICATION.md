# ML Pipeline — API Specification

**Version**: v1.2.2 | **Status**: Stub | **Last Updated**: March 2026

## 1. Overview

The `ml_pipeline` module is a reserved namespace for ML pipeline orchestration. Currently provides two MCP tools for pipeline definition and execution as pass-through stubs. For production workflow orchestration, see the `orchestrator` module.

## 2. Current State

This module has **no public Python exports** (`__init__.py` is empty). All functionality is exposed exclusively via MCP tools.

## 3. MCP Tools

### `ml_pipeline_create`

Creates a machine learning pipeline definition.

```python
ml_pipeline_create(name: str, steps: list[dict[str, Any]]) → dict[str, Any]
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | Pipeline name |
| `steps` | `list[dict]` | Ordered list of step configuration dictionaries |

**Returns**:

```python
{"status": "success", "pipeline": {"name": str, "steps": list}}
```

### `ml_pipeline_execute`

Executes a previously defined pipeline.

```python
ml_pipeline_execute(name: str, inputs: dict[str, Any]) → dict[str, Any]
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `name` | `str` | Pipeline name to execute |
| `inputs` | `dict` | Input data for the pipeline |

**Returns**:

```python
{"status": "success", "result": {"pipeline": str, "outputs": dict}}
```

> [!NOTE]
> Both tools are currently pass-through stubs that echo inputs. They do not perform actual ML operations or persist state.

## 4. Usage Example

```python
# Via MCP tool invocation
from codomyrmex.ml_pipeline.mcp_tools import ml_pipeline_create, ml_pipeline_execute

# Define a pipeline
result = ml_pipeline_create(
    name="text_classifier",
    steps=[
        {"name": "preprocess", "type": "tokenize", "config": {"max_length": 512}},
        {"name": "train", "type": "fine_tune", "config": {"epochs": 3}},
        {"name": "evaluate", "type": "metrics", "config": {"metrics": ["accuracy"]}},
    ],
)

# Execute it
output = ml_pipeline_execute(
    name="text_classifier",
    inputs={"data_path": "/data/train.csv"},
)
```

## 5. Related Modules

| Module | Relationship |
| :--- | :--- |
| `orchestrator` | General workflow orchestration (production-ready) |
| `feature_store` | Feature management and serving |
| `eval_harness` | Model evaluation pipeline |

## 6. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
