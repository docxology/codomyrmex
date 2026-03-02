# Agent Guidelines - Model Ops

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

ML model lifecycle management covering training data preprocessing, feature engineering, model scoring,
optimization, deployment, and versioning. Provides `ModelRegistry` for versioned model storage,
`FeatureStore` for centralized embedding management, `ModelEvaluator` for performance verification,
and `InferenceOptimizer` for production latency reduction. Three MCP tools expose scoring and
sanitization capabilities to PAI agents without requiring Python imports.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `ModelRegistry`, `FeatureStore`, `ModelEvaluator`, `InferenceOptimizer`, `FineTuningJob` |
| `model_registry.py` | Versioned model storage and retrieval (`register()`, `load()`) |
| `feature_store.py` | Centralized feature and embedding management |
| `model_evaluator.py` | Comprehensive model performance verification |
| `inference_optimizer.py` | Latency and cost reduction toolkit (quantization, etc.) |
| `fine_tuning/fine_tuning.py` | Managed fine-tuning orchestration (`FineTuningJob`) |
| `mcp_tools.py` | MCP tools: `model_ops_score_output`, `model_ops_sanitize_dataset`, `model_ops_list_scorers` |

## Key Classes

- **ModelRegistry** — Model versioning and storage management (`register()`, `load()`)
- **FeatureStore** — Centralized feature and embedding management (`push_features()`, `get_features()`)
- **ModelEvaluator** — Comprehensive model performance verification (`evaluate()`)
- **InferenceOptimizer** — Latency and cost reduction toolkit (`optimize()`)
- **FineTuningJob** — Managed fine-tuning orchestration

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `model_ops_score_output` | Score model output quality using a named scorer | SAFE |
| `model_ops_sanitize_dataset` | Sanitize a dataset by removing duplicates, nulls, and outliers | SAFE |
| `model_ops_list_scorers` | List all available output scorer names and their descriptions | SAFE |

## Agent Instructions

1. **Feature Reuse** — Always check the `FeatureStore` before regenerating embeddings or features
2. **Mandatory Evaluation** — Run `ModelEvaluator` on all new models before registration
3. **Optimize for Production** — Apply `InferenceOptimizer` tweaks (quantization, etc.) for high-traffic models
4. **Registry First** — Use `ModelRegistry` for all model versioning to ensure reproducibility

## Operating Contracts

- `ModelRegistry.register()` must be called before any `load()` for the same name+version
- `ModelEvaluator.evaluate()` returns a dict — check all keys before declaring production readiness
- `FeatureStore.push_features()` overwrites existing features for the same entity key
- `model_ops_score_output` is read-only and does not mutate state — safe to call repeatedly
- **DO NOT** import `ExperimentTracker` from the module root — it is not a public export

## Common Patterns

```python
from codomyrmex.model_ops import (
    ModelRegistry, FeatureStore, ModelEvaluator, InferenceOptimizer
)

# 1. Feature Engineering
fs = FeatureStore()
fs.push_features("user_123", {"embedding": [0.1, 0.2, 0.3]})

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
# Verify registry round-trip
registry = ModelRegistry()
registry.register("test_model", "1.0", dummy_model)
loaded = registry.load("test_model", "1.0")
assert loaded is not None

# Verify feature store
fs = FeatureStore()
fs.push_features("entity_1", {"score": 0.9})
features = fs.get_features("entity_1")
assert features["score"] == 0.9
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `model_ops_score_output`, `model_ops_sanitize_dataset`, `model_ops_list_scorers` | TRUSTED |
| **Architect** | Read + Design | `model_ops_list_scorers` — scorer catalog review, MLOps architecture design | OBSERVED |
| **QATester** | Validation | `model_ops_score_output`, `model_ops_list_scorers` — evaluation metric verification | OBSERVED |
| **Researcher** | Read-only | `model_ops_list_scorers`, `model_ops_score_output` — quality scoring for research analysis | SAFE |

### Engineer Agent
**Use Cases**: Deploying models during EXECUTE, running evaluations, sanitizing datasets, managing model registry.

### Architect Agent
**Use Cases**: Designing MLOps pipelines, reviewing evaluation frameworks, planning model versioning strategies.

### QATester Agent
**Use Cases**: Validating model evaluation results during VERIFY, confirming deployment health, testing scorer correctness.

### Researcher Agent
**Use Cases**: Scoring model output quality and inspecting scorer catalog during research analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
