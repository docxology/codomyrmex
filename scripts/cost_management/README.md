# Cost Management Scripts

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demo scripts for the `cost_management` module, which provides cost tracking, budget management, and spend categorization for cloud and compute resources.

## Purpose

These scripts demonstrate cost tracking lifecycle operations including creating cost trackers, setting budget periods, categorizing spend, and generating cost reports using the `CostTracker`, `BudgetManager`, and `JSONCostStore` components.

## Contents

| File | Description |
|------|-------------|
| `cost_management_demo.py` | Demonstrates cost tracking, budget management, and category-based spend analysis |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/cost_management/cost_management_demo.py
```

## Agent Usage

Agents should use these scripts to validate cost tracking integrations. The demo exercises `CostTracker`, `BudgetManager`, `CostCategory`, `BudgetPeriod`, and `JSONCostStore` classes.

## Related Module

- Source: `src/codomyrmex/cloud/cost_management/`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
