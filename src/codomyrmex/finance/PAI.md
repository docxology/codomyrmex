# Personal AI Infrastructure -- Finance Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Finance module is a **double-entry bookkeeping engine** for tracking financial operations within the Codomyrmex ecosystem. It provides account management with standard accounting types (Asset, Liability, Equity, Revenue, Expense), balanced transaction posting with normal-balance enforcement, and plain-text financial reports (balance tables, income statements, balance sheets).

## PAI Capabilities

### Double-Entry Bookkeeping

Create accounts and record transactions with automatic balance enforcement:

```python
from decimal import Decimal

from codomyrmex.finance import AccountType, Ledger

ledger = Ledger()
cash = ledger.create_account("Assets:Cash", AccountType.ASSET)
revenue = ledger.create_account("Revenue:Services", AccountType.REVENUE)

# Positive amounts are debits, negative amounts are credits; entries must sum to zero
ledger.post_transaction(
    [
        {"account_id": cash.id, "amount": Decimal("500.00")},
        {"account_id": revenue.id, "amount": Decimal("-500.00")},
    ],
    description="Service sale",
)

print(ledger.get_balance(cash.id))           # Decimal('500.00')
print(ledger.trial_balance()["balanced"])    # True
```

### Financial Visualization

Generate text reports for account balances and income:

```python
from codomyrmex.finance.visualization import balance_table, income_statement_text

accounts = list(ledger.accounts.values())
print(balance_table(accounts))
print(income_statement_text(accounts))
```

## Key Exports

| Export | Type | Purpose |
| --- | --- | --- |
| `Ledger` | Class | Double-entry bookkeeping engine with account and transaction management |
| `Transaction` | Dataclass | Balanced set of `TransactionEntry` legs (debits == credits) |
| `Account` | Class | Financial account with name, type, and running balance |
| `AccountType` | Enum | Account classifications: ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| `LedgerError` | Exception | Raised on invalid ledger operations |
| `finance.visualization.balance_table()` | Function | Text table of account balances |
| `finance.visualization.income_statement_text()` | Function | Text income statement from revenue and expense accounts |

## PAI Algorithm Phase Mapping

| Phase | Finance Module Contribution |
| --- | --- |
| **OBSERVE** | `get_balance()` and `trial_balance()` provide real-time financial state observation |
| **PLAN** | Account structure and transaction history inform budget planning and forecasting |
| **EXECUTE** | `post_transaction()` executes financial transactions with double-entry validation |
| **VERIFY** | `trial_balance()` verifies accounting consistency; text reports summarise state |
| **LEARN** | Transaction history and balance trends support financial pattern analysis |

## Architecture Role

**Application Layer** -- Domain-specific financial management module. Renders its own text reports via `finance.visualization`. Has no upward dependencies from other modules.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:

- Direct Python import: `from codomyrmex.finance import ...`
- CLI: `codomyrmex finance <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
