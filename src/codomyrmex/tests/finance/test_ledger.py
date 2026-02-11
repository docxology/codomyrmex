import pytest
from codomyrmex.finance.account import AccountType
from codomyrmex.finance.ledger import Ledger, Transaction, LedgerError

def test_ledger_initialization():
    ledger = Ledger()
    assert ledger._accounts == {}
    assert ledger._transactions == []

def test_create_account():
    ledger = Ledger()
    acc = ledger.create_account("Cash", AccountType.ASSET)
    assert acc.name == "Cash"
    assert acc.account_type == AccountType.ASSET
    assert acc.balance == 0.0

    with pytest.raises(LedgerError):
        ledger.create_account("Cash", AccountType.ASSET)

def test_record_transaction():
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    ledger.create_account("Revenue", AccountType.REVENUE)

    tx = Transaction(
        debit_account="Cash",
        credit_account="Revenue",
        amount=100.0,
        description="Software License Sale"
    )
    ledger.record(tx)

    assert ledger.get_balance("Cash") == 100.0
    assert ledger.get_balance("Revenue") == 100.0
    assert len(ledger._transactions) == 1

def test_invalid_transaction():
    ledger = Ledger()
    ledger.create_account("Cash", AccountType.ASSET)
    
    # Missing credit account
    tx = Transaction(
        debit_account="Cash",
        credit_account="Unknown",
        amount=50.0,
        description="Bad TX"
    )
    with pytest.raises(LedgerError):
        ledger.record(tx)
    
    # Negative amount
    tx_neg = Transaction(
        debit_account="Cash",
        credit_account="Cash", 
        amount=-10.0,
        description="Negative"
    )
    with pytest.raises(LedgerError):
        ledger.record(tx_neg)

def test_trial_balance():
    ledger = Ledger()
    ledger.create_account("Bank", AccountType.ASSET)
    ledger.create_account("Equity", AccountType.EQUITY)
    
    ledger.record(Transaction("Bank", "Equity", 1000.0, "Initial Investment"))
    assert ledger.trial_balance()
