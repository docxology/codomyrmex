# Codomyrmex Agents -- src/codomyrmex/finance/ledger

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Implements a double-entry bookkeeping general ledger following standard accounting principles. Every transaction must balance (total debits equal total credits), accounts are classified by type (asset, liability, equity, revenue, expense), and financial statements (balance sheet, income statement, trial balance) can be generated from recorded data.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `ledger.py` | `AccountType` | Enum of five standard account classifications: ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| `ledger.py` | `LedgerError` | Exception raised on validation failures (duplicate accounts, unbalanced transactions, missing accounts) |
| `ledger.py` | `Account` | Dataclass representing a named financial account with type, running balance, and creation timestamp |
| `ledger.py` | `TransactionEntry` | A single leg of a transaction affecting one account; positive amount is debit, negative is credit |
| `ledger.py` | `Transaction` | Atomic collection of balanced entries with an `is_balanced` property |
| `ledger.py` | `Ledger` | General ledger managing accounts, transactions, balance sheets, income statements, and trial balances |

## Operating Contracts

- `create_account` raises `LedgerError` if an account with the same name already exists.
- `post_transaction` validates that all referenced accounts exist and that entries sum to zero before applying.
- Balance updates follow normal-balance rules: Asset and Expense accounts increase with debits; Liability, Equity, and Revenue accounts increase with credits.
- `get_balance_sheet` returns assets, liabilities, equity totals with a `balanced` flag confirming the accounting equation holds.
- `get_income_statement` accepts optional date range filters and returns revenue, expenses, and net income.
- `trial_balance` sums all debit-normal and credit-normal accounts to verify the ledger is in balance.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Python stdlib (`uuid`, `logging`, `datetime`, `dataclasses`, `enum`)
- **Used by**: `finance.payroll` (payroll transactions may post to ledger accounts), financial reporting modules

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Siblings**: [forecasting](../forecasting/AGENTS.md) | [payroll](../payroll/AGENTS.md) | [taxes](../taxes/AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
