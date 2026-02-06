# Agent Guidelines - Model Ops

## Module Overview

ML model lifecycle: training, deployment, versioning, and monitoring.

## Key Classes

- **ModelRegistry** — Model versioning and storage
- **ModelDeployer** — Deploy models to endpoints
- **ExperimentTracker** — Track training experiments
- **ModelMonitor** — Monitor deployed models

## Agent Instructions

1. **Version models** — Every model gets a version
2. **Track experiments** — Log hyperparameters and metrics
3. **Validate before deploy** — Test on held-out data
4. **Monitor drift** — Watch for data/model drift
5. **Rollback ready** — Keep previous versions

## Common Patterns

```python
from codomyrmex.model_ops import (
    ModelRegistry, ExperimentTracker, ModelDeployer
)

# Track experiment
with ExperimentTracker.start("training_v1") as exp:
    exp.log_params({"lr": 0.01, "epochs": 100})
    model = train_model(...)
    exp.log_metrics({"accuracy": 0.95, "loss": 0.05})
    exp.log_model(model)

# Register model
registry = ModelRegistry()
registry.register(
    name="classifier",
    version="1.0.0",
    model=model,
    metadata={"framework": "pytorch"}
)

# Deploy model
deployer = ModelDeployer()
endpoint = deployer.deploy(
    model_uri="models:/classifier/1.0.0",
    instance_type="gpu.small"
)
```

## Testing Patterns

```python
# Verify registry
registry = ModelRegistry()
registry.register("test", "1.0", dummy_model)
loaded = registry.load("test", "1.0")
assert loaded is not None

# Verify experiment tracking
with ExperimentTracker.start("test") as exp:
    exp.log_metrics({"acc": 0.9})
    assert exp.get_metrics()["acc"] == 0.9
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
