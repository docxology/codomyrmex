# Synthetic Data Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

Template and structured synthetic data generation for ML training.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Generate training data for ML pipelines | `synth_generate_structured`, `synth_generate_classification` |
| **VERIFY** | Create test datasets for validation | `synth_generate_preference_pairs` |

## Key Exports

### Classes

- **`SyntheticDataGenerator`** -- Structured, classification, and preference pair generation
- **`DataSchema`** -- Schema definition for structured data fields
- **`TemplateGenerator`** -- Template-based text generation with variable substitution

## Quick Start

```python
from codomyrmex.synthetic_data import SyntheticDataGenerator, DataSchema

gen = SyntheticDataGenerator()

# Structured tabular data
schema = DataSchema(
    fields={"name": {"type": "str"}, "age": {"type": "int", "min": 18, "max": 65}},
    n_samples=100,
)
records = gen.generate_structured(schema, seed=42)

# Classification dataset
features, labels = gen.generate_classification(n_samples=1000, n_classes=3, seed=42)

# RLHF preference pairs
pairs = gen.generate_preference_pairs(n_pairs=500, seed=42)
```

## Directory Structure

- `generator.py` -- Core generator classes (SyntheticDataGenerator, DataSchema, TemplateGenerator)
- `mcp_tools.py` -- MCP tool definitions
- `__init__.py` -- Public API re-exports

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/synthetic_data/ -v
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
