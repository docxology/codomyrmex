"""Tests for the finance module.

Tests cover:
- Module import
- AccountType enum values
- Account creation and defaults
- Ledger account creation
- Ledger duplicate account raises
- Ledger get_account not found raises
- Transaction recording and balance updates
- Negative transaction amount raises
- Double-entry balance consistency
- Trial balance verification
"""

import pytest

from codomyrmex.finance.account import Account, AccountType
from codomyrmex.finance.ledger import Ledger, LedgerError, Transaction


@pytest.mark.unit
def test_module_import():
    """finance module is importable."""
    from codomyrmex import finance
    assert finance is not None


@pytest.mark.unit
def test_account_type_enum_values():
    """AccountType enum has five standard types."""
    assert AccountType.ASSET.name == "ASSET"
    assert AccountType.LIABILITY.name == "LIABILITY"
    assert AccountType.EQUITY.name == "EQUITY"
    assert AccountType.REVENUE.name == "REVENUE"
    assert AccountType.EXPENSE.name == "EXPENSE"


@pytest.mark.unit
def test_account_creation():
    """Account is created with zero balance."""
    acct = Account("Cash", AccountType.ASSET)
    assert acct.name == "Cash"
    assert acct.account_type == AccountType.ASSET
    assert acct.balance == 0.0


@pytest.mark.unit
def test_account_repr():
    """Account repr includes name and type."""
    acct = Account("Revenue", AccountType.REVENUE)
    r = repr(acct)
    assert "Revenue" in r
    assert "REVENUE" in r


@pytest.mark.unit
def test_ledger_create_account():
    """Ledger.create_account registers a new account."""
    ledger = Ledger()
    acct = ledger.create_account("Cash", AccountType.ASSET)
    assert acct.name == "Cash"
    assert ledger.get_account("Cash") is acct


@pytest.mark.unit
def test_ledger_duplicate_account_raises():
    """Ledger raises LedgerError on duplicate account name."""
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    with pytest.raises(LedgerError, match="already exists"):
        ledger.create_account("Cash", AccountType.ASSET)


@pytest.mark.unit
def test_ledger_get_account_not_found():
    """Ledger raises LedgerError for nonexistent account."""
    ledger = Ledger()
    with pytest.raises(LedgerError, match="not found"):
        ledger.get_account("Nonexistent")


@pytest.mark.unit
def test_ledger_record_transaction():
    """Ledger records a transaction and updates balances correctly."""
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    ledger.create_account("Revenue", AccountType.REVENUE)

    txn = Transaction(
        debit_account="Cash",
        credit_account="Revenue",
        amount=1000.0,
        description="Sale proceeds",
    )
    ledger.record(txn)

    # Asset debit increases balance
    assert ledger.get_balance("Cash") == 1000.0
    # Revenue credit increases balance
    assert ledger.get_balance("Revenue") == 1000.0


@pytest.mark.unit
def test_ledger_negative_amount_raises():
    """Ledger raises LedgerError for negative transaction amounts."""
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    ledger.create_account("Expense", AccountType.EXPENSE)

    txn = Transaction(
        debit_account="Expense",
        credit_account="Cash",
        amount=-50.0,
        description="Invalid",
    )
    with pytest.raises(LedgerError, match="negative"):
        ledger.record(txn)


@pytest.mark.unit
def test_ledger_expense_debit():
    """Recording expense: debit to expense, credit from cash."""
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    ledger.create_account("Office Supplies", AccountType.EXPENSE)

    # First fund the cash account
    ledger.create_account("Capital", AccountType.EQUITY)
    fund_txn = Transaction(
        debit_account="Cash",
        credit_account="Capital",
        amount=5000.0,
        description="Initial funding",
    )
    ledger.record(fund_txn)

    # Record expense
    expense_txn = Transaction(
        debit_account="Office Supplies",
        credit_account="Cash",
        amount=200.0,
        description="Bought supplies",
    )
    ledger.record(expense_txn)

    assert ledger.get_balance("Office Supplies") == 200.0
    assert ledger.get_balance("Cash") == 4800.0


@pytest.mark.unit
def test_ledger_trial_balance():
    """Ledger.trial_balance returns True when books are balanced."""
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    ledger.create_account("Revenue", AccountType.REVENUE)

    txn = Transaction(
        debit_account="Cash",
        credit_account="Revenue",
        amount=500.0,
        description="Service",
    )
    ledger.record(txn)
    assert ledger.trial_balance() is True


@pytest.mark.unit
def test_transaction_is_frozen():
    """Transaction dataclass is immutable (frozen)."""
    txn = Transaction(
        debit_account="Cash",
        credit_account="Revenue",
        amount=100.0,
        description="Test",
    )
    with pytest.raises(AttributeError):
        txn.amount = 200.0
