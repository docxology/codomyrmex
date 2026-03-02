# Agent Guidelines - Model Ops

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

ML model lifecycle: training, feature engineering, optimization, deployment, and versioning.

## Key Classes

- **ModelRegistry** — Model versioning and storage management
- **FeatureStore** — Centralized feature and embedding management
- **ModelEvaluator** — Comprehensive model performance verification
- **InferenceOptimizer** — Latency and cost reduction toolkit
- **FineTuningJob** — Managed fine-tuning orchestration

## Agent Instructions

1. **Feature Reuse** — Always check the `FeatureStore` before regenerating embeddings or features
2. **Mandatory Evaluation** — Run `ModelEvaluator` on all new models before registration
3. **Optimize for Production** — Apply `InferenceOptimizer` tweaks (quantization, etc.) for high-traffic models
4. **registry.register** — Use the registry for all model versioning to ensure reproducibility

## Common Patterns

```python
from codomyrmex.model_ops import (
    ModelRegistry, FeatureStore, ModelEvaluator, InferenceOptimizer
)

# 1. Feature Engineering
fs = FeatureStore()
fs.push_features("user_123", {"embedding": [0.1, 0.2, ...]})

# 2. Evaluation
evaluator = ModelEvaluator()
results = evaluator.evaluate(model_id="v1_candidate", test_dataset=ds)
print(f"Accuracy: {results['accuracy']}")

# 3. Optimization
optimizer = InferenceOptimizer()
optimized_model = optimizer.optimize("v1_candidate", target="latency")

# 4. Registration
registry = ModelRegistry()
registry.register(
    name="production_model",
    version="2.1.0",
    model_path=optimized_model,
    metadata={"eval_results": results}
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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Model deployment, evaluation, monitoring, A/B testing, model registry management | TRUSTED |
| **Architect** | Read + Design | Model lifecycle design, evaluation framework review, MLOps architecture | OBSERVED |
| **QATester** | Validation | Model evaluation metric verification, inference correctness, deployment health | OBSERVED |

### Engineer Agent
**Use Cases**: Deploying models during EXECUTE, running evaluations, managing model registry.

### Architect Agent
**Use Cases**: Designing MLOps pipelines, reviewing evaluation frameworks, planning model versioning.

### QATester Agent
**Use Cases**: Validating model evaluation results during VERIFY, confirming deployment health.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
