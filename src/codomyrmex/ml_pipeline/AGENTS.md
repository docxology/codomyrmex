# ML Pipeline -- Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Context

The ML Pipeline module provides tools for building, executing, and managing machine learning pipelines. Pipelines are defined as named sequences of steps, where each step is a configuration dictionary. Agents use this module to create reproducible training and inference workflows.

## MCP Tools

| Tool | Inputs | Outputs | Description |
|------|--------|---------|-------------|
| `ml_pipeline_create` | `name: str`, `steps: list[dict]` | `{"status": "success", "pipeline": {...}}` | Creates a new ML pipeline with named steps |
| `ml_pipeline_execute` | `name: str`, `inputs: dict` | `{"status": "success", "result": {...}}` | Executes a previously created pipeline with provided inputs |

### Parameter Details

**`ml_pipeline_create`**
- `name`: Unique identifier for the pipeline (e.g., `"training-v2"`)
- `steps`: Ordered list of step definitions. Each dict should contain step-specific configuration (e.g., `{"type": "preprocess", "config": {...}}`)

**`ml_pipeline_execute`**
- `name`: Name of an existing pipeline to run
- `inputs`: Dictionary of input data or parameters required by the pipeline steps

## Agent Use Cases

### 1. Training Pipeline Setup
An Engineer agent creates a multi-step training pipeline with preprocessing, training, and evaluation steps, then executes it with a dataset reference.

### 2. Experiment Comparison
An Engineer agent creates multiple pipeline variants with different step configurations, executes each, and compares the output results to select the best configuration.

### 3. Architecture Review
An Architect agent inspects pipeline definitions to verify step ordering, identify missing validation steps, and confirm that the pipeline structure follows best practices.

## Example Workflow

```
# Step 1: Create a training pipeline
ml_pipeline_create(
    name="sentiment-classifier-v1",
    steps=[
        {"type": "preprocess", "config": {"tokenizer": "bpe", "max_length": 512}},
        {"type": "train", "config": {"model": "bert-base", "epochs": 3, "lr": 2e-5}},
        {"type": "evaluate", "config": {"metrics": ["accuracy", "f1"]}}
    ]
)

# Step 2: Execute the pipeline with inputs
ml_pipeline_execute(
    name="sentiment-classifier-v1",
    inputs={"dataset": "reviews-2026Q1", "split": "train"}
)

# Step 3: Check result status and outputs
# Response: {"status": "success", "result": {"pipeline": "sentiment-classifier-v1", "outputs": {...}}}
```

## Error Handling

| Scenario | Expected Behavior | Agent Action |
|----------|-------------------|--------------|
| Pipeline name already exists | Tool returns error status | Use a unique name or version suffix |
| Empty steps list | Tool returns error status | Provide at least one step definition |
| Pipeline not found on execute | Tool returns error status | Verify pipeline was created first |
| Invalid step configuration | Tool returns error status | Check step dict structure matches expected schema |

All MCP tools return `{"status": "error", "message": "..."}` on failure -- agents should always check the `status` field.

## Constraints

- Pipeline names must be unique within the current session
- Steps are executed in the order provided during creation
- No partial execution -- if a step fails, the pipeline reports failure
- Zero-mock policy applies: tests must use real pipeline objects, not stubs

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full -- create, execute, configure pipelines | ml_pipeline_create, ml_pipeline_execute | TRUSTED |
| **Architect** | Read + Architecture review | Read-only (inspect pipeline definitions) | SAFE |
| **QATester** | Validation + output verification | ml_pipeline_execute (read results) | SAFE |
| **Researcher** | Read-only -- study pipeline configurations | None | OBSERVED |
