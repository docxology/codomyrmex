# Data Lineage Scripts

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demo scripts for the `data_lineage` module, which tracks data flow through processing pipelines and performs impact analysis on data transformations.

## Purpose

These scripts demonstrate the full data lineage lifecycle: registering data nodes, defining transformation edges, building lineage graphs, and running impact analysis to determine downstream effects of data changes.

## Contents

| File | Description |
|------|-------------|
| `data_lineage_demo.py` | Demonstrates lineage tracking with `LineageTracker` and impact analysis with `ImpactAnalyzer` |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/data_lineage/data_lineage_demo.py
```

## Agent Usage

Agents analyzing data pipelines should use these scripts to validate lineage graph construction. The demo exercises `LineageTracker`, `ImpactAnalyzer`, `NodeType`, and `EdgeType` components.

## Related Module

- Source: `src/codomyrmex/data_lineage/`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
