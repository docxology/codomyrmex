# ML Pipeline

Tools for building, executing, and managing machine learning pipelines.

> Source module: [`src/codomyrmex/ml_pipeline/`](../../../src/codomyrmex/ml_pipeline/)

## Key Capabilities

- **Pipeline Definition**: Create named pipelines with ordered step sequences
- **Step Management**: Configure individual steps with type-specific parameters
- **Pipeline Execution**: Run pipelines with provided input data and collect results
- **Input/Output Tracking**: Validate and track data flowing between pipeline steps

## MCP Tools

| Tool | Description |
|------|-------------|
| `ml_pipeline_create` | Creates a new ML pipeline with named steps |
| `ml_pipeline_execute` | Executes a previously created pipeline with provided inputs |

## Quick Start

```python
# Via MCP tools
ml_pipeline_create(
    name="classifier-v1",
    steps=[
        {"type": "preprocess", "config": {"tokenizer": "bpe"}},
        {"type": "train", "config": {"model": "bert-base", "epochs": 3}}
    ]
)

ml_pipeline_execute(name="classifier-v1", inputs={"dataset": "train-set"})
```

## References

- [Source README](../../../src/codomyrmex/ml_pipeline/README.md)
- [AGENTS.md](../../../src/codomyrmex/ml_pipeline/AGENTS.md)
- [PAI.md](../../../src/codomyrmex/ml_pipeline/PAI.md)
