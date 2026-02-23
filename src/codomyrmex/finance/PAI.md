# Personal AI Infrastructure -- Finance Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Finance module is a **double-entry bookkeeping engine** for tracking financial operations within the Codomyrmex ecosystem. It provides account management with standard accounting types (Asset, Liability, Equity, Revenue, Expense), immutable transaction recording with normal-balance enforcement, and visualization of financial state through bar and line charts.

## PAI Capabilities

### Double-Entry Bookkeeping

Create accounts and record transactions with automatic balance enforcement:

```python
from codomyrmex.finance.ledger import Ledger, Transaction
from codomyrmex.finance.account import AccountType

ledger = Ledger()
ledger.create_account("Cash", AccountType.ASSET)
ledger.create_account("Revenue", AccountType.REVENUE)

tx = Transaction(debit_account="Cash", credit_account="Revenue", amount=500.0, description="Service sale")
ledger.record(tx)

print(ledger.get_balance("Cash"))     # 500.0
print(ledger.trial_balance())          # True
```

### Financial Visualization

Generate charts for account balances and transaction volume:

```python
from codomyrmex.finance.visualization import plot_account_balances, plot_transaction_volume

bar_chart = plot_account_balances(ledger)
line_chart = plot_transaction_volume(ledger)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Ledger` | Class | Double-entry bookkeeping engine with account and transaction management |
| `Transaction` | Frozen Dataclass | Immutable record of a debit/credit financial event |
| `Account` | Class | Financial account with name, type, and running balance |
| `AccountType` | Enum | Account classifications: ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE |
| `LedgerError` | Exception | Raised on invalid ledger operations |
| `plot_account_balances()` | Function | Bar chart of all account balances |
| `plot_transaction_volume()` | Function | Line chart of transaction amounts over time |

## PAI Algorithm Phase Mapping

| Phase | Finance Module Contribution |
|-------|---------------------------|
| **OBSERVE** | `get_balance()` and `trial_balance()` provide real-time financial state observation |
| **PLAN** | Account structure and transaction history inform budget planning and forecasting |
| **EXECUTE** | `record()` executes financial transactions with double-entry validation |
| **VERIFY** | `trial_balance()` verifies accounting consistency; visualization charts verify state visually |
| **LEARN** | Transaction history and balance trends support financial pattern analysis |

## Architecture Role

**Application Layer** -- Domain-specific financial management module. Depends on the `visualization` module for chart rendering. Has no upward dependencies from other modules.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
