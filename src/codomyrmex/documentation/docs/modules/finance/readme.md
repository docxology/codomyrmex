# Finance Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Complete financial management system for autonomous agents and user businesses. Provides double-entry ledger, tax compliance, payroll processing, and financial forecasting.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Query financial data from ledger and accounts | Direct Python import |
| **THINK** | Analyze financial metrics and identify trends | Direct Python import |
| **PLAN** | Generate financial projections and forecasts | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Architect agent uses Forecaster during PLAN to generate projections, while agents query the Ledger during OBSERVE for real-time financial state.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Ledger` | Class | Double-entry bookkeeping engine |
| `Transaction` | Class | Immutable financial record |
| `Account` | Class | Chart of accounts management |
| `Forecaster` | Class | Financial modeling and prediction |
| `TaxCalculator` | Class | Tax estimation and compliance |
| `TaxResult` | Class | Tax calculation result data model |
| `PayrollProcessor` | Class | Employee payment processing |
| `PayStub` | Class | Pay stub data model |

### Submodules

| Submodule | Purpose |
|-----------|---------|
| `ledger/` | Core accounting engine (double-entry, journal, trial balance) |
| `taxes/` | Tax compliance, estimation, and reporting |
| `payroll/` | Payment processing and stub generation |
| `forecasting/` | Financial modeling, projections, and trend analysis |

## Quick Start

```python
from codomyrmex.finance import Ledger, Transaction, Forecaster, TaxCalculator

# Double-entry bookkeeping
ledger = Ledger()
ledger.record(Transaction(amount=100.00, debit="Assets:Cash", credit="Revenue:Sales"))
balance = ledger.trial_balance()

# Financial forecasting
forecaster = Forecaster()
projection = forecaster.project(ledger, months=12)

# Tax calculation
tax = TaxCalculator(jurisdiction="US")
result = tax.estimate(ledger, year=2026)
```

## Architecture

```
finance/
├── __init__.py        # All exports
├── ledger/            # Double-entry accounting
├── taxes/             # Tax compliance
├── payroll/           # Payment processing
├── forecasting/       # Financial modeling
└── tests/             # Zero-Mock tests
```

## Navigation

- **Extended Docs**: [docs/modules/finance/](../../../docs/modules/finance/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
