# Inference Optimization Module — Agent Coordination

## Purpose

Model optimization techniques including quantization and batching.

## Key Capabilities

- **QuantizationType**: Types of quantization.
- **BatchingStrategy**: Strategies for batching requests.
- **OptimizationConfig**: Configuration for inference optimization.
- **InferenceStats**: Statistics for inference performance.
- **InferenceRequest**: A single inference request.
- `cache_hit_rate()`: Get cache hit rate.
- `age_ms()`: Get request age in milliseconds.
- `get()`: Get cached result.

## Agent Usage Patterns

```python
from codomyrmex.inference_optimization import QuantizationType

# Agent initializes inference optimization
instance = QuantizationType()
```

## Integration Points

- **Source**: [src/codomyrmex/inference_optimization/](../../../src/codomyrmex/inference_optimization/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k inference_optimization -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
