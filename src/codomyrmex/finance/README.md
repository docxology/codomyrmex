# Finance Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Complete financial management system for autonomous agents and user businesses. Provides double-entry ledger, tax compliance, payroll processing, and financial forecasting.

## Installation

```bash
uv pip install codomyrmex
```

## Key Exports

### Ledger

- **`Ledger`** — Double-entry bookkeeping engine
- **`Transaction`** — Immutable financial record
- **`Account`** — Chart of accounts management

### Submodules

- `ledger/` — Core accounting engine
- `taxes/` — Compliance and estimation
- `payroll/` — Payment processing
- `forecasting/` — Financial modeling

## Quick Start

```python
from codomyrmex.finance import Ledger, Transaction

ledger = Ledger()
ledger.record(Transaction(amount=100.00, debit="Assets:Cash", credit="Revenue:Sales"))
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [Parent](../README.md)
