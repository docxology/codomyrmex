# Synthetic Data - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Generate synthetic datasets for ML training, testing, and benchmarking without requiring real data access.

## Functional Requirements

- Structured data generation with type-aware fields (str, int, float, bool, choice, text)
- Classification datasets with configurable class balance and feature dimensions
- Preference pair generation for RLHF/DPO training
- Template-based text generation with variable substitution
- Deterministic output via random seed control

## Core Classes

| Class | Description |
|-------|-------------|
| `SyntheticDataGenerator` | Central generator for all data types |
| `DataSchema` | Field type definitions for structured data |
| `TemplateGenerator` | Template-based text generation |

## Field Types

| Type | Parameters | Output |
|------|-----------|--------|
| `str` | `length` | Random lowercase string |
| `int` | `min`, `max` | Random integer in range |
| `float` | `min`, `max` | Random float in range |
| `bool` | -- | True or False |
| `choice` | `options` | Random pick from options |
| `text` | `n_words` | Multi-word text from word lists |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
