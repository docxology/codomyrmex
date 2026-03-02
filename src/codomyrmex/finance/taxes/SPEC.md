# Tax Calculation -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Progressive (marginal) tax calculation engine with configurable bracket definitions and deduction support. Computes total tax, effective rate, marginal rate, and per-bracket breakdown. Ships with simplified 2024-era US federal brackets as defaults.

## Architecture

`TaxCalculator` processes income through sorted brackets sequentially, taxing each slice at the bracket's marginal rate. Bracket definitions are validated and sorted at construction time. The `TaxResult` dataclass captures the full computation output including per-bracket detail.

## Key Classes

### `TaxResult` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `gross_income` | `float` | Income before deductions |
| `taxable_income` | `float` | Income after deductions |
| `total_tax` | `float` | Total tax owed (rounded to 2 decimals) |
| `effective_rate` | `float` | Overall rate: tax / income (rounded to 6 decimals) |
| `marginal_rate` | `float` | Highest bracket rate applied |
| `bracket_breakdown` | `list[dict]` | Per-bracket detail: min, max, rate, taxable_amount, tax |

### `TaxCalculator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `brackets: list[dict] \| None` | -- | Initialize with custom or default US federal brackets |
| `calculate_tax` | `income: float` | `TaxResult` | Compute progressive tax with full bracket breakdown |
| `apply_deductions` | `income, deductions: list[dict]` | `float` | Reduce income by deduction amounts (floor at zero) |

### Default Brackets

| Bracket Min | Bracket Max | Rate |
|------------|-------------|------|
| 0 | 11,600 | 10% |
| 11,600 | 47,150 | 12% |
| 47,150 | 100,525 | 22% |
| 100,525 | 191,950 | 24% |
| 191,950 | 243,725 | 32% |
| 243,725 | 609,350 | 35% |
| 609,350 | infinity | 37% |

## Dependencies

- **Internal**: None
- **External**: None (Python stdlib: `dataclasses`)

## Constraints

- Income must be non-negative; `TaxError` raised otherwise.
- Each bracket must have `min`, `max`, and `rate` keys; rates must be in [0, 1].
- Brackets are auto-sorted by `min` regardless of input order.
- Deduction amounts must be non-negative; `TaxError` raised on negative values.
- Taxable income after deductions is floored at zero.
- Zero-mock: real computations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `TaxError` raised for: negative income, invalid bracket definitions, invalid rates, negative deductions.
- All errors logged before propagation.
