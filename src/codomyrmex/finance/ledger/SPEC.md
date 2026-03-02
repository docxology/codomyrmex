# Double-Entry Ledger -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Full double-entry bookkeeping general ledger implementing standard accounting principles. Every transaction must balance (sum of debits equals sum of credits), accounts are classified into five types, and financial statements can be generated from the recorded data.

## Architecture

The `Ledger` class manages a collection of `Account` objects and an ordered list of `Transaction` records. Each `Transaction` contains multiple `TransactionEntry` legs. Balance updates follow normal-balance rules (asset/expense accounts increase with debits; liability/equity/revenue accounts increase with credits).

## Key Classes

### `AccountType` (Enum)

| Value | Normal Balance | Description |
|-------|---------------|-------------|
| `ASSET` | Debit | Cash, receivables, equipment |
| `LIABILITY` | Credit | Payables, loans |
| `EQUITY` | Credit | Owner's equity, retained earnings |
| `REVENUE` | Credit | Sales, service income |
| `EXPENSE` | Debit | Costs, salaries, rent |

### `Account` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID-based unique identifier |
| `name` | `str` | Human-readable account name |
| `account_type` | `AccountType` | Determines debit/credit behaviour |
| `balance` | `float` | Current running balance |

### `Ledger`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_account` | `name, account_type` | `Account` | Create and register a new account (UUID assigned) |
| `post_transaction` | `entries: list[dict], description` | `Transaction` | Post a balanced transaction; validates accounts and balance |
| `get_balance` | `account_id` | `float` | Return current balance for an account |
| `get_balance_sheet` | -- | `dict` | Assets, liabilities, equity with `balanced` flag |
| `get_income_statement` | `start?, end?` | `dict` | Revenue, expenses, net income for optional date range |
| `trial_balance` | -- | `dict` | Debit/credit totals with `balanced` flag |

## Dependencies

- **Internal**: None
- **External**: None (Python stdlib: `uuid`, `logging`, `datetime`, `dataclasses`, `enum`)

## Constraints

- Account names must be unique within a ledger; `LedgerError` raised on duplicate.
- Transaction entries must reference existing account IDs.
- Transaction entry amounts must sum to zero (tolerance: `1e-9`).
- Balance sheet equation: `total_assets == total_liabilities + total_equity`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `LedgerError` raised for: duplicate account names, unknown account IDs, unbalanced transactions.
- All errors logged via `logging` before propagation.
