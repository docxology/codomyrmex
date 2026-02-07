# Model Ops Module — Agent Coordination

## Purpose

Model Operations module for Codomyrmex.

## Key Capabilities

- **Dataset**: A dataset for ML model operations.
- **DatasetSanitizer**: Utilities for cleaning and filtering datasets.
- **FineTuningJob**: Fine-tuning job management.
- **Evaluator**: Model output evaluator with customizable metrics.
- `exact_match_metric()`: Calculate exact match ratio (strips whitespace before comparison).
- `length_ratio_metric()`: Calculate average length ratio.
- `validate()`: Validate the dataset.

## Agent Usage Patterns

```python
from codomyrmex.model_ops import Dataset

# Agent initializes model ops
instance = Dataset()
```

## Integration Points

- **Source**: [src/codomyrmex/model_ops/](../../../src/codomyrmex/model_ops/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
