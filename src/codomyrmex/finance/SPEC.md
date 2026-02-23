# Finance — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Complete financial management: double-entry bookkeeping, tax compliance, payroll, and financial forecasting.

## Functional Requirements

### Ledger

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `Ledger()` | Constructor | Create empty ledger |
| `ledger.record(txn)` | `record(Transaction) → None` | Record a balanced transaction |
| `ledger.trial_balance()` | `→ dict[str, Decimal]` | Compute trial balance |

### Transactions

| Constraint | Description |
|------------|-------------|
| Immutability | Transactions cannot be modified after creation |
| Balance | `debit_amount == credit_amount` (enforced at record time) |
| Account naming | Must follow `Category:Subcategory` format |

### Tax and Payroll

| Interface | Description |
|-----------|-------------|
| `TaxCalculator(jurisdiction)` | Tax estimation for a given jurisdiction |
| `PayrollProcessor()` | Employee payment processing and stub generation |
| `Forecaster()` | Financial projection and trend modeling |

## Non-Functional Requirements

- **Precision**: All monetary values use `Decimal` (no floating point)
- **Auditability**: Full transaction log with timestamps and audit trail
- **Atomicity**: Ledger records are atomic — balanced or rejected

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
