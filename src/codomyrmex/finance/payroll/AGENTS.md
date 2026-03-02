# Codomyrmex Agents -- src/codomyrmex/finance/payroll

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Processes payroll by calculating net pay from gross salary, applying federal income tax (via `TaxCalculator`), Social Security and Medicare withholdings (FICA), and employee-specific deductions. Generates detailed pay stubs for each pay period.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `processor.py` | `PayrollError` | Exception raised on invalid payroll inputs (negative salary, unknown pay period) |
| `processor.py` | `PayStub` | Dataclass representing a complete earnings statement with gross, withholdings, deductions, and net pay |
| `processor.py` | `PayrollProcessor` | Payroll engine that calculates withholdings and generates pay stubs |
| `processor.py` | `PayrollProcessor.calculate_pay` | Computes federal tax, Social Security, Medicare, and net pay for a single period |
| `processor.py` | `PayrollProcessor.generate_pay_stub` | Creates a `PayStub` for an employee including custom deductions (401k, insurance, etc.) |

## Operating Contracts

- `PayrollProcessor` accepts an optional `TaxCalculator`; defaults to a calculator with standard US brackets if none provided.
- `calculate_pay` annualises the gross salary to compute federal tax, then pro-rates back to the period.
- Social Security is capped at the wage base ($168,600 for 2024); Medicare has no cap.
- Supported pay periods: `weekly`, `biweekly`, `semimonthly`, `monthly`, `annual`.
- `generate_pay_stub` requires employee dicts with `name` and `id` keys; raises `PayrollError` on missing fields.
- Additional employee deductions are subtracted from net pay after standard withholdings.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `finance.taxes.calculator.TaxCalculator`, `finance.taxes.calculator.TaxResult`
- **Used by**: Payroll reporting, financial dashboards

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Siblings**: [forecasting](../forecasting/AGENTS.md) | [ledger](../ledger/AGENTS.md) | [taxes](../taxes/AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
