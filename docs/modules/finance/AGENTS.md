# Finance Module — Agent Coordination

## Purpose

Finance Module for Codomyrmex.

Provides double-entry bookkeeping, tax compliance, payroll processing,
and financial forecasting.

Submodules:
    ledger -- Double-entry bookkeeping engine
    forecasting -- Time-series forecasting (moving average, exponential smoothing, linear trend)
    taxes -- Progressive tax calculation with bracket support
    payroll -- Payroll processing with tax withholding and pay-stub generation

## Key Capabilities

- **`Ledger`** — Double-entry bookkeeping engine
- **`Transaction`** — Immutable financial record
- **`Account`** — Chart of accounts management
- `ledger/` — Core accounting engine
- `taxes/` — Compliance and estimation
- `payroll/` — Payment processing
- `forecasting/` — Financial modeling

## Agent Usage Patterns

```python
from codomyrmex.finance import Ledger, Transaction

ledger = Ledger()
ledger.record(Transaction(amount=100.00, debit="Assets:Cash", credit="Revenue:Sales"))
```

## Key Components

| Export | Type |
|--------|------|
| `AccountType` | Public API |
| `Account` | Public API |
| `TransactionEntry` | Public API |
| `Transaction` | Public API |
| `Ledger` | Public API |
| `LedgerError` | Public API |
| `Forecaster` | Public API |
| `TaxCalculator` | Public API |
| `TaxResult` | Public API |
| `PayrollProcessor` | Public API |
| `PayStub` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `account.py` | Primary account types in double-entry bookkeeping. |
| `ledger.py` | Immutable record of a financial event. |
| `visualization.py` | Generates a bar chart of account balances. |

## Submodules

- `forecasting/` — Forecasting
- `ledger/` — Ledger
- `payroll/` — Payroll
- `taxes/` — Taxes

## Integration Points

- **Source**: [src/codomyrmex/finance/](../../../src/codomyrmex/finance/)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k finance -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
