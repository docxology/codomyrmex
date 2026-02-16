# Cost Management Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Spend tracking, budgeting, and cost optimization for AI/cloud infrastructure. Provides a `CostTracker` to record and aggregate cost entries across categories (LLM inference, compute, storage, network, API calls), a `BudgetManager` for creating budgets with configurable periods and alert thresholds, and pluggable storage backends for persistence.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Enums

- **`CostCategory`** -- Categories of costs: LLM_INFERENCE, LLM_EMBEDDING, COMPUTE, STORAGE, NETWORK, API_CALLS, OTHER
- **`BudgetPeriod`** -- Budget time periods: HOURLY, DAILY, WEEKLY, MONTHLY

### Data Classes

- **`CostEntry`** -- A single cost record with amount, category, resource ID, tags, and timestamp; includes `to_dict()` serialization
- **`Budget`** -- A budget allocation with amount, period, optional category filter, tags filter, and configurable alert thresholds (default: 50%, 80%, 90%, 100%); computes period start boundaries
- **`CostSummary`** -- Aggregated cost summary with totals broken down by category, resource, and tag
- **`BudgetAlert`** -- A budget alert containing budget ID, threshold, current spend, and computed utilization percentage with a human-readable message

### Storage

- **`CostStore`** -- Abstract base class for cost storage backends with `save_entry()` and `get_entries()` methods
- **`InMemoryCostStore`** -- Thread-safe in-memory implementation of CostStore for development and testing

### Services

- **`CostTracker`** -- Main cost tracking service; records cost entries with auto-generated IDs and produces aggregated summaries filtered by period, date range, or category
- **`BudgetManager`** -- Budget management and alerting; creates budgets, checks utilization against thresholds, emits alerts when thresholds are crossed, and validates whether a proposed spend fits within budget limits

## Directory Contents

- `models.py` -- Data models (CostEntry, Budget, etc.)
- `stores.py` -- Storage backends (CostStore, InMemoryCostStore)
- `tracker.py` -- Core logic (CostTracker, BudgetManager)
- `__init__.py` -- Public API re-exports
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Quick Start

```python
from codomyrmex.cost_management import CostCategory, BudgetPeriod, CostEntry

# Initialize CostCategory
instance = CostCategory()
```

## Navigation

- **Full Documentation**: [docs/modules/cost_management/](../../../docs/modules/cost_management/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
