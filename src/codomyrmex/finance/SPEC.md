# Finance — Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

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

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `InsufficientDataError` | Not enough historical data for forecasting (e.g., < 3 data points for trend) | Provide more transaction history; `Forecaster` requires minimum 3 periods |
| `CalculationError` | Numerical overflow during tax/payroll computation (extremely large amounts) | Use `Decimal` with explicit precision; check for values exceeding `Decimal("999999999999.99")` |
| `RateError` | Missing exchange rate for currency conversion | Pre-load exchange rates via `RateProvider.load(date, currency_pair)` before calculations |
| `BalanceError` | Transaction `debit_amount != credit_amount` at record time | Ensure all transactions are balanced before calling `ledger.record()` |
| `AccountError` | Account name does not follow `Category:Subcategory` format | Use the format `"Assets:Bank"`, `"Expenses:Software"`, etc. |
| `ImmutabilityError` | Attempt to modify or delete a recorded transaction | Transactions are immutable; post a correcting entry instead |
| `JurisdictionError` | `TaxCalculator` initialized with an unsupported jurisdiction code | Check `TaxCalculator.supported_jurisdictions()` before construction |

## Data Contracts

### Transaction Input

```python
# Transaction schema (required for ledger.record())
{
    "date": str,                     # ISO 8601 date, e.g., "2026-03-01"
    "description": str,              # Human-readable memo, max 256 chars
    "entries": [
        {
            "account": str,          # "Category:Subcategory" format
            "debit": Decimal | None, # Debit amount or None
            "credit": Decimal | None # Credit amount or None
        },
        ...  # At least 2 entries; sum(debits) must equal sum(credits)
    ],
    "metadata": {                    # Optional
        "reference": str,            # External reference number
        "tags": list[str],           # Classification tags
    }
}
```

### Trial Balance Output

```python
# ledger.trial_balance() output
{
    "as_of": str,                    # ISO 8601 timestamp
    "accounts": {
        "Assets:Bank": Decimal,      # Positive = debit balance
        "Liabilities:AP": Decimal,   # Negative = credit balance
        ...
    },
    "total_debits": Decimal,         # Sum of all debit balances
    "total_credits": Decimal,        # Sum of all credit balances (absolute)
    "balanced": bool,                # True if debits == credits
}
```

### Portfolio Schema

```python
# Portfolio for risk analysis
{
    "name": str,                     # Portfolio identifier
    "positions": [
        {
            "symbol": str,           # Instrument symbol
            "quantity": Decimal,     # Number of units held
            "cost_basis": Decimal,   # Average cost per unit
            "current_price": Decimal,# Latest market price
            "currency": str,         # ISO 4217 currency code
        },
        ...
    ],
    "base_currency": str,            # Portfolio reporting currency
}
```

### Risk Metrics Output

```python
# Forecaster.risk_metrics(portfolio) output
{
    "total_value": Decimal,          # Current portfolio market value
    "total_pnl": Decimal,           # Unrealized profit/loss
    "pnl_percent": Decimal,         # PnL as percentage
    "var_95": Decimal,              # Value at Risk (95% confidence)
    "max_drawdown": Decimal,        # Maximum peak-to-trough decline
    "sharpe_ratio": Decimal | None, # Risk-adjusted return (None if < 30 days data)
    "currency": str,                # Reporting currency
}
```

## Performance SLOs

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| `ledger.record(txn)` | < 5ms | Validation + append; no disk I/O until flush |
| `ledger.trial_balance()` | < 100ms | Aggregation over all entries; cached after first call |
| `TaxCalculator.estimate()` | < 200ms | Depends on jurisdiction complexity |
| `PayrollProcessor.process()` | < 500ms | Per-employee calculation |
| Portfolio risk calculation | < 500ms | For up to 1,000 positions |
| `Forecaster.project(periods=12)` | < 2s | 12-month projection with Monte Carlo simulation |

**Precision Guarantees:**
- All monetary values: `Decimal` with 2 decimal places minimum
- No floating point operations on money -- ever
- Rounding mode: `ROUND_HALF_EVEN` (banker's rounding)

## Design Constraints

1. **Decimal-Only Arithmetic**: All monetary calculations use `decimal.Decimal`. No `float` or `int` representation of currency amounts. This is enforced at the type level.
2. **Immutable Ledger**: Once recorded, transactions cannot be modified or deleted. Corrections are made via reversing entries. The full audit trail is preserved.
3. **Atomicity**: `ledger.record()` either records all entries of a transaction or none. Partial recording is impossible.
4. **No Silent Failures**: Unbalanced transactions raise `BalanceError` immediately. Invalid accounts raise `AccountError`. No auto-correction.
5. **Auditability**: Every transaction carries a timestamp, user/agent ID, and optional metadata. Trial balances are reproducible from the entry log.
6. **Currency Isolation**: Multi-currency operations require explicit conversion through `RateProvider`. No implicit currency conversion.

## PAI Algorithm Integration

| Phase | Usage | Example |
|-------|-------|---------|
| **OBSERVE** | Read current financial state | `ledger.trial_balance()` to assess account positions |
| **THINK** | Analyze risk metrics and trends | `forecaster.risk_metrics(portfolio)` to evaluate exposure |
| **PLAN** | Model future scenarios | `forecaster.project(periods=6)` for cash flow projections |
| **EXECUTE** | Record transactions and process payroll | `ledger.record(txn)` for bookkeeping entries |
| **VERIFY** | Confirm books are balanced | Assert `trial_balance()["balanced"] is True` after operations |
| **LEARN** | Track financial patterns over time | Store monthly summaries in `agentic_memory` for trend analysis |

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
