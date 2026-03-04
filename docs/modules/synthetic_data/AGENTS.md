# Synthetic Data Generator -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides template-based and schema-driven synthetic data generation for ML training pipelines. Supports structured records, classification datasets, and RLHF/DPO preference pairs.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `synth_generate_structured` | Generate structured synthetic data from a schema definition | Standard | synthetic_data |
| `synth_generate_classification` | Generate synthetic classification data with configurable class balance | Standard | synthetic_data |
| `synth_generate_preference_pairs` | Generate preference pairs for RLHF/DPO training | Standard | synthetic_data |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Generate synthetic training data for ML experiments |
| VERIFY | QA Agent | Validate data distributions and class balance in generated datasets |


## Agent Instructions

1. Define schema fields with type specs: {'age': {'type': 'int', 'min': 18, 'max': 65}}
2. class_balance supports 'balanced' and 'imbalanced' distributions for classification data


## Navigation

- [Source README](../../src/codomyrmex/synthetic_data/README.md) | [SPEC.md](SPEC.md)
