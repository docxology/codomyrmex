import pytest
from codomyrmex.finance.account import AccountType
from codomyrmex.finance.ledger import Ledger, LedgerError


def test_ledger_initialization():
    ledger = Ledger()
    assert ledger.accounts == {}
    assert ledger.transactions == []


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
    cash = ledger.create_account("Cash", AccountType.ASSET)
    revenue = ledger.create_account("Revenue", AccountType.REVENUE)

    tx = ledger.post_transaction(
        entries=[
            {"account_id": cash.id, "amount": 100.0, "description": "Debit cash"},
            {"account_id": revenue.id, "amount": -100.0, "description": "Credit revenue"},
        ],
        description="Software License Sale",
    )

    assert tx.description == "Software License Sale"
    assert len(ledger.transactions) == 1


def test_invalid_transaction():
    ledger = Ledger()
    cash = ledger.create_account("Cash", AccountType.ASSET)

    # Missing account
    with pytest.raises(LedgerError):
        ledger.post_transaction(
            entries=[
                {"account_id": cash.id, "amount": 50.0, "description": "Debit"},
                {"account_id": "nonexistent-uuid", "amount": 50.0, "description": "Credit"},
            ],
            description="Bad TX",
        )


def test_trial_balance():
    ledger = Ledger()
    bank = ledger.create_account("Bank", AccountType.ASSET)
    equity = ledger.create_account("Equity", AccountType.EQUITY)

    ledger.post_transaction(
        entries=[
            {"account_id": bank.id, "amount": 1000.0, "description": "Debit bank"},
            {"account_id": equity.id, "amount": -1000.0, "description": "Credit equity"},
        ],
        description="Initial Investment",
    )
    result = ledger.trial_balance()
    assert isinstance(result, dict)
