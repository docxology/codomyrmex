# Agent Guidelines - Synthetic Data

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Generate synthetic datasets for ML training: structured tabular data, classification datasets, and RLHF preference pairs.

## Key Classes

- **SyntheticDataGenerator** -- All-in-one generator for structured, classification, and preference data
- **DataSchema** -- Type-aware schema for structured field generation
- **TemplateGenerator** -- Text generation with variable-filled templates

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `synth_generate_structured` | Generate structured records from a schema | Safe |
| `synth_generate_classification` | Generate classification features and labels | Safe |
| `synth_generate_preference_pairs` | Generate RLHF/DPO preference pairs | Safe |

## Agent Instructions

1. **Use seeds** -- Always set seed for reproducible datasets
2. **Schema design** -- Define field types explicitly (str, int, float, bool, choice, text)
3. **Class balance** -- Use "balanced" for evaluation, "imbalanced" for real-world simulation

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | All synth tools | TRUSTED |
| **Researcher** | Full | All synth tools -- dataset creation for experiments | SAFE |
| **QATester** | Validation | `synth_generate_structured` -- test data generation | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
