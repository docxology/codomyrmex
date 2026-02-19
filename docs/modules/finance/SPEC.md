# Finance — Functional Specification

**Module**: `codomyrmex.finance`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Finance Module for Codomyrmex.

Provides double-entry bookkeeping, tax compliance, payroll processing,
and financial forecasting.

Submodules:
    ledger -- Double-entry bookkeeping engine
    forecasting -- Time-series forecasting (moving average, exponential smoothing, linear trend)
    taxes -- Progressive tax calculation with bracket support
    payroll -- Payroll processing with tax withholding and pay-stub generation

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `account.py` | Primary account types in double-entry bookkeeping. |
| `ledger.py` | Immutable record of a financial event. |
| `visualization.py` | Generates a bar chart of account balances. |

### Submodule Structure

- `forecasting/` — Forecasting
- `ledger/` — Ledger
- `payroll/` — Payroll
- `taxes/` — Taxes

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `AccountType`
- `Account`
- `TransactionEntry`
- `Transaction`
- `Ledger`
- `LedgerError`
- `Forecaster`
- `TaxCalculator`
- `TaxResult`
- `PayrollProcessor`
- `PayStub`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k finance -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/finance/)
