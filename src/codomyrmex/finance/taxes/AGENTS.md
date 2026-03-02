# Codomyrmex Agents -- src/codomyrmex/finance/taxes

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Implements progressive (marginal) tax calculation with configurable bracket definitions and deduction support. Computes total tax, effective rate, marginal rate, and per-bracket breakdown using ordinary bracket-based computation. Ships with simplified 2024-era US federal brackets as defaults.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `calculator.py` | `DEFAULT_BRACKETS` | Module-level list of 7 simplified US federal tax brackets (10% through 37%) |
| `calculator.py` | `TaxError` | Exception raised on invalid inputs (negative income, bad bracket definitions, invalid rates) |
| `calculator.py` | `TaxResult` | Dataclass containing gross_income, taxable_income, total_tax, effective_rate, marginal_rate, and bracket_breakdown |
| `calculator.py` | `TaxCalculator` | Progressive tax engine with bracket-based computation and deduction application |
| `calculator.py` | `TaxCalculator.calculate_tax` | Computes tax through all applicable brackets, returns `TaxResult` with full breakdown |
| `calculator.py` | `TaxCalculator.apply_deductions` | Reduces gross income by deduction amounts (floor at zero), returning taxable income |

## Operating Contracts

- `TaxCalculator` validates brackets at construction: each must have `min`, `max`, and `rate` keys; rates must be between 0 and 1.
- Brackets are automatically sorted by `min` value regardless of input order.
- `calculate_tax` processes brackets sequentially, taxing each income slice at the bracket's marginal rate.
- `effective_rate` is `total_tax / income` (zero if income is zero).
- `apply_deductions` accepts a list of deduction dicts with `name`, `amount`, and optional `type`; negative amounts raise `TaxError`.
- All monetary results are rounded to 2 decimal places; effective rates to 6 decimal places.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Python stdlib only (`dataclasses`)
- **Used by**: `finance.payroll.processor.PayrollProcessor` (imports `TaxCalculator` and `TaxResult` for federal withholding)

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Siblings**: [forecasting](../forecasting/AGENTS.md) | [ledger](../ledger/AGENTS.md) | [payroll](../payroll/AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
