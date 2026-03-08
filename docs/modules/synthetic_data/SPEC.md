# Synthetic Data Generator Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides template-based and schema-driven synthetic data generation for ML training pipelines. Supports structured records, classification datasets, and RLHF/DPO preference pairs.

## Functional Requirements

1. Schema-driven structured data generation with typed field specifications
2. Classification dataset generation with configurable feature dimensions and class balance
3. Preference pair generation for RLHF/DPO alignment training pipelines


## Interface

```python
from codomyrmex.synthetic_data import SyntheticDataGenerator, DataSchema, TemplateGenerator

gen = SyntheticDataGenerator()
records = gen.generate_structured(DataSchema(fields={"age": {"type": "int", "min": 18, "max": 65}}))
features, labels = gen.generate_classification(n_samples=1000, n_classes=3)
pairs = gen.generate_preference_pairs(n_pairs=500)
```

## Exports

SyntheticDataGenerator, DataSchema, TemplateGenerator

## Navigation

- [Source README](../../src/codomyrmex/synthetic_data/README.md) | [AGENTS.md](AGENTS.md)
