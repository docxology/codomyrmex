# Finance Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Complete financial management system for autonomous agents and user businesses. Provides double-entry ledger, tax compliance, payroll processing, and financial forecasting.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`Ledger`** -- Double-entry bookkeeping engine.
- **`Transaction`** -- Immutable financial record.
- **`Account`** -- Chart of accounts management.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `ledger` | Core accounting engine |
| `taxes` | Compliance and estimation |
| `payroll` | Payment processing |
| `forecasting` | Financial modeling |

## Quick Start

```python
from codomyrmex.finance import Ledger

ledger = Ledger()
ledger.record(Transaction(amount=100.00, debit="Assets:Cash", credit="Revenue:Sales"))
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Ledger` | Double-entry bookkeeping engine |
| `Transaction` | Immutable financial record |
| `Account` | Chart of accounts management |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k finance -v
```

## Related Modules

- [Governance](../governance/README.md)

## Navigation

- **Source**: [src/codomyrmex/finance/](../../../src/codomyrmex/finance/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/finance/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/finance/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
