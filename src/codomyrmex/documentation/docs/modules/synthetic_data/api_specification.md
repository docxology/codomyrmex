# Synthetic Data - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `synthetic_data` module provides template-based and LLM-powered synthetic data generation for training, testing, and augmentation purposes.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `SyntheticDataGenerator` | Main generator orchestrating data creation from schema definitions |
| `TemplateGenerator` | Template-based generator using string interpolation and rules |
| `DataSchema` | Schema definition for synthetic datasets (fields, types, constraints) |

## 3. Usage Example

```python
from codomyrmex.synthetic_data import SyntheticDataGenerator, DataSchema

schema = DataSchema(fields={
    "name": {"type": "string", "pattern": "faker.name"},
    "age": {"type": "int", "min": 18, "max": 80},
    "score": {"type": "float", "min": 0.0, "max": 1.0},
})

gen = SyntheticDataGenerator(schema)
dataset = gen.generate(n=1000)
print(f"Generated {len(dataset)} records")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
