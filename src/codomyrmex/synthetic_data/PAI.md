# Personal AI Infrastructure -- Synthetic Data Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Synthetic Data module generates training datasets for ML pipelines. It supports
structured tabular data, classification datasets with configurable class balance,
and preference pairs for RLHF/DPO alignment training.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.synth_generate_structured` | Generate structured records from schema | Safe | synthetic_data |
| `codomyrmex.synth_generate_classification` | Generate classification features/labels | Safe | synthetic_data |
| `codomyrmex.synth_generate_preference_pairs` | Generate RLHF/DPO preference pairs | Safe | synthetic_data |

## PAI Algorithm Phase Mapping

| Phase | Contribution | Key Functions |
|-------|-------------|---------------|
| **BUILD** (4/7) | Generate training data for ML workflows | `generate_structured()`, `generate_classification()` |
| **VERIFY** (6/7) | Create test datasets for validation | `generate_preference_pairs()` |
| **LEARN** (7/7) | Generate data for learning experiments | All generators |

## Architecture Role

**Application Layer** -- Provides synthetic data for ML training and evaluation workflows.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
