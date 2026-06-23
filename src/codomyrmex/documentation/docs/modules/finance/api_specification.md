# Finance - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Finance module. The primary purpose of this API is to provide a double-entry bookkeeping engine with account management, transaction recording, and financial visualization capabilities for autonomous agents and user businesses.

## Endpoints / Functions / Interfaces

### Enum: `AccountType`

- **Description**: Primary account types in double-entry bookkeeping, following standard accounting classification.
- **Module**: `codomyrmex.finance.account`
- **Values**:
    - `ASSET` - Resources owned (normal debit balance)
    - `LIABILITY` - Obligations owed (normal credit balance)
    - `EQUITY` - Owner's stake (normal credit balance)
    - `REVENUE` - Income earned (normal credit balance)
    - `EXPENSE` - Costs incurred (normal debit balance)

### Class: `Account`

- **Description**: Represents a financial account in the chart of accounts. Each account has a name, type, and running balance.
- **Module**: `codomyrmex.finance.account`
- **Parameters/Arguments** (constructor):
    - `name` (str): The account name (must be unique within a ledger)
    - `account_type` (AccountType): The classification of the account
- **Attributes**:
    - `name` (str): Account name
    - `account_type` (AccountType): Account classification
    - `balance` (float): Current balance, initialized to `0.0`
- **Methods**:
    - `__repr__() -> str`: Returns `Account(name='Cash', type=ASSET)`.

### Class: `Transaction` (frozen dataclass)

- **Description**: Immutable record of a financial event. Each transaction debits one account and credits another for a given amount, enforcing double-entry consistency.
- **Module**: `codomyrmex.finance.ledger`
- **Parameters/Arguments** (constructor):
    - `debit_account` (str): Name of the account to debit
    - `credit_account` (str): Name of the account to credit
    - `amount` (float): Transaction amount (must be non-negative)
    - `description` (str): Human-readable description of the transaction
    - `timestamp` (datetime, optional): When the transaction occurred. Defaults to `datetime.now()`
    - `id` (UUID, optional): Unique identifier. Auto-generated via `uuid4()` if not provided

### Class: `LedgerError`

- **Description**: Base exception for all ledger operations. Raised when accounts are not found, duplicate accounts are created, or transaction amounts are negative.
- **Module**: `codomyrmex.finance.ledger`
- **Inherits**: `Exception`

### Class: `Ledger`

- **Description**: Double-entry bookkeeping engine. Manages a chart of accounts and an ordered list of transactions, enforcing accounting rules (non-negative amounts, account existence, normal balance rules).
- **Module**: `codomyrmex.finance.ledger`
- **Parameters/Arguments** (constructor): None
- **Methods**:
    - `create_account(name: str, account_type: AccountType) -> Account`: Register a new account. Raises `LedgerError` if an account with the same name already exists.
    - `get_account(name: str) -> Account`: Retrieve an account by name. Raises `LedgerError` if not found.
    - `record(transaction: Transaction) -> None`: Record a double-entry transaction. Validates that the amount is non-negative and both accounts exist. Updates balances according to normal balance rules (assets/expenses increase on debit; liabilities/equity/revenue increase on credit). Raises `LedgerError` on validation failure.
    - `get_balance(account_name: str) -> float`: Returns the current balance of the named account. Raises `LedgerError` if account not found.
    - `trial_balance() -> bool`: Verifies that total debits equal total credits across all recorded transactions. Returns `True` if balanced (within floating-point tolerance of 1e-9).

### Function: `plot_account_balances(ledger: Ledger) -> BarPlot`

- **Description**: Generates a bar chart of all account balances in the ledger.
- **Module**: `codomyrmex.finance.visualization`
- **Parameters/Arguments**:
    - `ledger` (Ledger): The ledger instance to visualize
- **Returns/Response**: `BarPlot` - A bar chart with account names on the x-axis and balances on the y-axis, titled "Account Balances".

### Function: `plot_transaction_volume(ledger: Ledger) -> LinePlot`

- **Description**: Generates a line chart of transaction amounts over time (indexed by transaction order).
- **Module**: `codomyrmex.finance.visualization`
- **Parameters/Arguments**:
    - `ledger` (Ledger): The ledger instance to visualize
- **Returns/Response**: `LinePlot` - A line chart of transaction amounts by index, titled "Transaction Volume (Since {start_date})".

## Data Models

### Transaction (frozen dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `debit_account` | `str` | required | Name of the account to debit |
| `credit_account` | `str` | required | Name of the account to credit |
| `amount` | `float` | required | Transaction amount (non-negative) |
| `description` | `str` | required | Human-readable description |
| `timestamp` | `datetime` | `datetime.now()` | When the transaction occurred |
| `id` | `UUID` | auto-generated | Unique identifier |

## Authentication & Authorization

Not applicable for this internal finance module.

## Rate Limiting

Not applicable for this internal finance module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
