# ML Pipeline — API Specification

**Version**: v1.3.0 | **Status**: Experimental | **Last Updated**: July 2026

## 1. Overview

The `ml_pipeline` module provides two stateless receipt-producing functions
that are available through both the Python package root and MCP discovery.
Despite the historical `execute` name, the current implementation echoes
inputs and does not run an ML workload. For executable workflow orchestration,
see the `orchestrator` module.

## 2. Current State

`codomyrmex.ml_pipeline.__all__` explicitly exports:

- `ml_pipeline_create`
- `ml_pipeline_execute`

The same function objects carry `@mcp_tool()` metadata in `mcp_tools.py`.

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
> Both functions are pass-through adapters. They do not validate steps,
> persist pipeline state, or perform ML operations.

## 4. Usage Example

```python
# Via MCP tool invocation
from codomyrmex.ml_pipeline import ml_pipeline_create, ml_pipeline_execute

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
| `eval_harness` | Model evaluation pipeline |

## 6. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
