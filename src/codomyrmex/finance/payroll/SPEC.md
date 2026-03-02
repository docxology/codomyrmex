# Payroll Processing -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Calculates net pay from gross salary by applying federal income tax (via `TaxCalculator`), Social Security and Medicare (FICA) withholdings, and employee-specific deductions. Generates detailed pay stubs for each pay period.

## Architecture

`PayrollProcessor` uses composition with `TaxCalculator` for tax computation. Gross salary is annualised to compute federal tax, then pro-rated back to the pay period. FICA rates are applied directly per period. The `PayStub` dataclass captures the complete earnings statement.

## Key Classes

### `PayStub` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `employee_name` | `str` | Employee name |
| `employee_id` | `str` | Employee identifier |
| `pay_period` | `str` | Period label (e.g., "Jan 2024 (monthly)") |
| `gross_pay` | `float` | Total pay before deductions |
| `federal_tax` | `float` | Federal income tax withheld |
| `social_security` | `float` | Social Security withholding |
| `medicare` | `float` | Medicare withholding |
| `other_deductions` | `dict[str, float]` | Additional deductions (401k, insurance, etc.) |
| `net_pay` | `float` | Take-home pay after all deductions |

### `PayrollProcessor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `tax_calculator?` | -- | Initialize with optional `TaxCalculator`; defaults to US brackets |
| `calculate_pay` | `gross_salary, pay_period?` | `dict` | Compute withholdings and net pay for a period |
| `generate_pay_stub` | `employee: dict, period: dict` | `PayStub` | Create a full pay stub with custom deductions |

### FICA Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `SOCIAL_SECURITY_RATE` | 0.062 | Employee share of Social Security |
| `SOCIAL_SECURITY_WAGE_BASE` | 168,600 | Annual cap on Social Security wages |
| `MEDICARE_RATE` | 0.0145 | Employee share of Medicare (no cap) |

## Supported Pay Periods

| Period | Periods/Year |
|--------|-------------|
| `weekly` | 52 |
| `biweekly` | 26 |
| `semimonthly` | 24 |
| `monthly` | 12 |
| `annual` | 1 |

## Dependencies

- **Internal**: `finance.taxes.calculator.TaxCalculator`, `finance.taxes.calculator.TaxResult`
- **External**: None (Python stdlib only)

## Constraints

- Gross salary must be non-negative; `PayrollError` raised otherwise.
- Employee dict must contain `name` and `id` keys.
- Social Security taxable amount is capped at wage base pro-rated to the pay period.
- Zero-mock: real computations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `PayrollError` raised for negative salary, unknown pay period, or missing employee fields.
- All errors logged before propagation.
