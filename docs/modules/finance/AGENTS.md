# Agent Instructions for `codomyrmex.finance`

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Context

The Finance module provides double-entry accounting, tax compliance, payroll processing, and financial forecasting. All financial operations use immutable `Transaction` records and must maintain balanced ledger states.

## Usage Guidelines

1. **Importing**: Import from the module root.

   ```python
   from codomyrmex.finance import Ledger, Transaction, Account, Forecaster, TaxCalculator, PayrollProcessor
   ```

2. **Double-Entry Principle**: Every `Transaction` must have equal debit and credit amounts. The `Ledger` enforces this invariant.

3. **Account Chart**: Use standard account naming: `Assets:*`, `Liabilities:*`, `Revenue:*`, `Expenses:*`, `Equity:*`.

4. **Zero-Mock Policy**: Tests must use real `Ledger` instances with actual transactions. No mocking of financial calculations or storage.

5. **Tax Calculations**: `TaxCalculator` requires a `jurisdiction` parameter. Results are advisory — always validate with a professional.

## Key Files

| File | Purpose |
|------|---------|
| `ledger/` | Core accounting (Ledger, Transaction, Account, Journal) |
| `taxes/` | TaxCalculator, TaxResult |
| `payroll/` | PayrollProcessor, PayStub |
| `forecasting/` | Financial prediction models |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md) | [Parent](../AGENTS.md)
