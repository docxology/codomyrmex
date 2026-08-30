<!-- readme: generated -->

# finance

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/finance/`

## Overview

Finance Module for Codomyrmex.

Provides double-entry bookkeeping, tax compliance, payroll processing,
and financial forecasting.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `ledger` | -- Double-entry bookkeeping engine |
| `forecasting` | -- Time-series forecasting (moving average, exponential smoothing, linear trend) |
| `taxes` | -- Progressive tax calculation with bracket support |
| `payroll` | -- Payroll processing with tax withholding and pay-stub generation |

## Public Exports

`finance` exports 14 public symbols via `__all__`:

`Account`, `AccountType`, `ForecastError`, `Forecaster`, `Ledger`, `LedgerError`, `PayStub`, `PayrollError`, `PayrollProcessor`, `TaxCalculator`, `TaxError`, `TaxResult`, `Transaction`, `TransactionEntry`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../finance/](../../../../finance/)
