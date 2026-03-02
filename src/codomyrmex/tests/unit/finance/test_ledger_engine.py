"""
Unit tests for finance.ledger and finance.account — Zero-Mock compliant.

Covers finance/ledger/ledger.py:
  AccountType (5 enum string values),
  Account dataclass (balance, repr),
  TransactionEntry (account_id, amount, description default),
  Transaction (is_balanced, non-balanced),
  LedgerError (is Exception),
  Ledger (create_account duplicate guard, post_transaction balance check /
    missing-account guard / empty-entries guard / normal-balance rules,
    get_balance, get_balance_sheet, get_income_statement with/without dates,
    trial_balance, __repr__).

Also covers finance/account.py:
  AccountType enum (auto values),
  Account (debit/credit normal-balance rules, freeze/unfreeze, to_dict, repr),
  AccountChart (create, get, find_by_name/code, by_type, totals, summary).
"""

import pytest

from codomyrmex.finance.account import (
    Account as OOPAccount,
)
from codomyrmex.finance.account import (
    AccountChart,
)
from codomyrmex.finance.account import (
    AccountType as OOPAccountType,
)

# ── finance/ledger/ledger.py ───────────────────────────────────────────
from codomyrmex.finance.ledger import (
    Account,
    AccountType,
    Ledger,
    LedgerError,
    Transaction,
    TransactionEntry,
)


@pytest.mark.unit
class TestLedgerAccountType:
    def test_five_members(self):
        assert len(AccountType) == 5

    def test_asset_value(self):
        assert AccountType.ASSET.value == "asset"

    def test_liability_value(self):
        assert AccountType.LIABILITY.value == "liability"

    def test_equity_value(self):
        assert AccountType.EQUITY.value == "equity"

    def test_revenue_value(self):
        assert AccountType.REVENUE.value == "revenue"

    def test_expense_value(self):
        assert AccountType.EXPENSE.value == "expense"


@pytest.mark.unit
class TestLedgerAccount:
    def test_balance_default_zero(self):
        a = Account(id="a1", name="Cash", account_type=AccountType.ASSET)
        assert a.balance == pytest.approx(0.0)

    def test_repr_contains_name(self):
        a = Account(id="x", name="Bank", account_type=AccountType.ASSET)
        assert "Bank" in repr(a)


@pytest.mark.unit
class TestTransactionEntry:
    def test_fields_stored(self):
        entry = TransactionEntry(account_id="acc-1", amount=100.0)
        assert entry.account_id == "acc-1"
        assert entry.amount == pytest.approx(100.0)

    def test_description_default_empty(self):
        entry = TransactionEntry(account_id="acc-1", amount=50.0)
        assert entry.description == ""

    def test_description_stored(self):
        entry = TransactionEntry(account_id="acc-1", amount=50.0, description="wages")
        assert entry.description == "wages"


@pytest.mark.unit
class TestTransaction:
    def test_is_balanced_true(self):
        entries = [
            TransactionEntry("a", 100.0),
            TransactionEntry("b", -100.0),
        ]
        tx = Transaction(id="tx1", entries=entries, description="sale")
        assert tx.is_balanced is True

    def test_is_balanced_false(self):
        entries = [TransactionEntry("a", 100.0)]
        tx = Transaction(id="tx1", entries=entries, description="unbalanced")
        assert tx.is_balanced is False

    def test_timestamp_set(self):
        tx = Transaction(id="tx1", entries=[], description="test")
        assert tx.timestamp is not None

    def test_description_stored(self):
        tx = Transaction(id="tx1", entries=[], description="my description")
        assert tx.description == "my description"


@pytest.mark.unit
class TestLedgerError:
    def test_is_exception(self):
        assert isinstance(LedgerError("oops"), Exception)

    def test_message(self):
        e = LedgerError("bad thing")
        assert "bad thing" in str(e)


@pytest.mark.unit
class TestLedger:
    def _make_ledger_with_cash_and_revenue(self):
        ledger = Ledger()
        cash = ledger.create_account("Cash", AccountType.ASSET)
        revenue = ledger.create_account("Sales Revenue", AccountType.REVENUE)
        return ledger, cash, revenue

    def test_create_account_returns_account(self):
        ledger = Ledger()
        acc = ledger.create_account("Cash", AccountType.ASSET)
        assert isinstance(acc, Account)
        assert acc.name == "Cash"

    def test_create_account_stored_by_id(self):
        ledger = Ledger()
        acc = ledger.create_account("Cash", AccountType.ASSET)
        assert acc.id in ledger.accounts

    def test_create_duplicate_name_raises(self):
        ledger = Ledger()
        ledger.create_account("Cash", AccountType.ASSET)
        with pytest.raises(LedgerError, match="already exists"):
            ledger.create_account("Cash", AccountType.LIABILITY)

    def test_post_transaction_balanced(self):
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        tx = ledger.post_transaction(
            [{"account_id": cash.id, "amount": 1000},
             {"account_id": revenue.id, "amount": -1000}],
            description="Sale",
        )
        assert isinstance(tx, Transaction)
        assert tx.is_balanced is True

    def test_post_transaction_stored(self):
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        ledger.post_transaction(
            [{"account_id": cash.id, "amount": 500},
             {"account_id": revenue.id, "amount": -500}],
            description="Sale",
        )
        assert len(ledger.transactions) == 1

    def test_post_transaction_empty_entries_raises(self):
        ledger = Ledger()
        with pytest.raises(LedgerError):
            ledger.post_transaction([], description="empty")

    def test_post_transaction_unknown_account_raises(self):
        ledger = Ledger()
        with pytest.raises(LedgerError, match="not found"):
            ledger.post_transaction(
                [{"account_id": "nonexistent", "amount": 100}],
                description="bad",
            )

    def test_post_transaction_unbalanced_raises(self):
        ledger, cash, _ = self._make_ledger_with_cash_and_revenue()
        with pytest.raises(LedgerError, match="balance"):
            ledger.post_transaction(
                [{"account_id": cash.id, "amount": 100}],
                description="unbalanced",
            )

    def test_asset_balance_increases_on_debit(self):
        """Asset normal-debit: positive amount increases balance."""
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        ledger.post_transaction(
            [{"account_id": cash.id, "amount": 1000},
             {"account_id": revenue.id, "amount": -1000}],
            description="Sale",
        )
        assert ledger.get_balance(cash.id) == pytest.approx(1000.0)

    def test_revenue_balance_increases_on_credit(self):
        """Revenue credit-normal: negative entry increases balance (balance -= entry.amount)."""
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        ledger.post_transaction(
            [{"account_id": cash.id, "amount": 500},
             {"account_id": revenue.id, "amount": -500}],
            description="Sale",
        )
        # balance -= (-500) → balance = 500
        assert ledger.get_balance(revenue.id) == pytest.approx(500.0)

    def test_get_balance_missing_raises(self):
        ledger = Ledger()
        with pytest.raises(LedgerError):
            ledger.get_balance("missing")

    def test_get_balance_sheet_keys(self):
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        sheet = ledger.get_balance_sheet()
        for key in ("assets", "liabilities", "equity", "total_assets",
                    "total_liabilities", "total_equity", "balanced"):
            assert key in sheet

    def test_balance_sheet_balanced_empty_ledger(self):
        ledger = Ledger()
        sheet = ledger.get_balance_sheet()
        assert sheet["balanced"] is True

    def test_get_income_statement_keys(self):
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        statement = ledger.get_income_statement()
        for key in ("revenue", "expenses", "total_revenue", "total_expenses", "net_income"):
            assert key in statement

    def test_get_income_statement_with_date_filter(self):
        from datetime import datetime, timedelta
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        ledger.post_transaction(
            [{"account_id": cash.id, "amount": 500},
             {"account_id": revenue.id, "amount": -500}],
            description="past sale",
        )
        future = datetime.now() + timedelta(days=365)
        statement = ledger.get_income_statement(end=future)
        assert statement["total_revenue"] >= 0

    def test_trial_balance_keys(self):
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        tb = ledger.trial_balance()
        for key in ("balances", "total_debits", "total_credits", "balanced"):
            assert key in tb

    def test_trial_balance_balanced_after_transaction(self):
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        ledger.post_transaction(
            [{"account_id": cash.id, "amount": 200},
             {"account_id": revenue.id, "amount": -200}],
            description="Sale",
        )
        tb = ledger.trial_balance()
        assert tb["balanced"] is True

    def test_repr_contains_name(self):
        ledger = Ledger("My Company")
        assert "My Company" in repr(ledger)

    def test_name_default(self):
        ledger = Ledger()
        assert "General Ledger" in repr(ledger) or ledger.name == "General Ledger"

    def test_entry_description_forwarded(self):
        ledger, cash, revenue = self._make_ledger_with_cash_and_revenue()
        tx = ledger.post_transaction(
            [{"account_id": cash.id, "amount": 100, "description": "debit leg"},
             {"account_id": revenue.id, "amount": -100, "description": "credit leg"}],
            description="With descriptions",
        )
        assert tx.entries[0].description == "debit leg"
        assert tx.entries[1].description == "credit leg"


# ── finance/account.py ────────────────────────────────────────────────


@pytest.mark.unit
class TestOOPAccountType:
    def test_five_members(self):
        assert len(OOPAccountType) == 5

    def test_asset_exists(self):
        _ = OOPAccountType.ASSET

    def test_expense_is_debit_normal(self):
        acc = OOPAccount("Wages", OOPAccountType.EXPENSE)
        assert acc.is_debit_normal is True

    def test_liability_not_debit_normal(self):
        acc = OOPAccount("Loans", OOPAccountType.LIABILITY)
        assert acc.is_debit_normal is False


@pytest.mark.unit
class TestOOPAccount:
    def test_name_and_type_stored(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        assert a.name == "Cash"
        assert a.account_type == OOPAccountType.ASSET

    def test_balance_init_zero(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        assert a.balance == pytest.approx(0.0)

    def test_id_auto_generated(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        assert len(a.id) > 0

    def test_debit_asset_increases_balance(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        a.debit(200.0)
        assert a.balance == pytest.approx(200.0)

    def test_credit_asset_decreases_balance(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        a.balance = 500.0
        a.credit(100.0)
        assert a.balance == pytest.approx(400.0)

    def test_credit_revenue_increases_balance(self):
        a = OOPAccount("Sales", OOPAccountType.REVENUE)
        a.credit(300.0)
        assert a.balance == pytest.approx(300.0)

    def test_debit_revenue_decreases_balance(self):
        a = OOPAccount("Sales", OOPAccountType.REVENUE)
        a.balance = 500.0
        a.debit(100.0)
        assert a.balance == pytest.approx(400.0)

    def test_debit_negative_raises(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        with pytest.raises(ValueError):
            a.debit(-10.0)

    def test_credit_negative_raises(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        with pytest.raises(ValueError):
            a.credit(-10.0)

    def test_debit_when_frozen_raises(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        a.freeze()
        with pytest.raises(ValueError):
            a.debit(10.0)

    def test_credit_when_frozen_raises(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        a.freeze()
        with pytest.raises(ValueError):
            a.credit(10.0)

    def test_unfreeze_allows_operations(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        a.freeze()
        a.unfreeze()
        a.debit(50.0)
        assert a.balance == pytest.approx(50.0)

    def test_to_dict_keys(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        d = a.to_dict()
        for key in ("id", "name", "code", "type", "balance", "frozen"):
            assert key in d

    def test_to_dict_type_is_name_string(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        assert a.to_dict()["type"] == "ASSET"

    def test_repr_contains_name(self):
        a = OOPAccount("Cash", OOPAccountType.ASSET)
        assert "Cash" in repr(a)


@pytest.mark.unit
class TestAccountChart:
    def test_create_returns_account(self):
        chart = AccountChart()
        acc = chart.create("Cash", OOPAccountType.ASSET)
        assert isinstance(acc, OOPAccount)
        assert acc.name == "Cash"

    def test_get_by_id(self):
        chart = AccountChart()
        acc = chart.create("Cash", OOPAccountType.ASSET)
        assert chart.get(acc.id) is acc

    def test_get_missing_returns_none(self):
        assert AccountChart().get("missing") is None

    def test_find_by_name(self):
        chart = AccountChart()
        chart.create("Bank", OOPAccountType.ASSET)
        found = chart.find_by_name("Bank")
        assert found is not None and found.name == "Bank"

    def test_find_by_name_missing(self):
        assert AccountChart().find_by_name("X") is None

    def test_find_by_code(self):
        chart = AccountChart()
        chart.create("Cash", OOPAccountType.ASSET, code="1001")
        found = chart.find_by_code("1001")
        assert found is not None

    def test_find_by_code_missing(self):
        assert AccountChart().find_by_code("9999") is None

    def test_by_type(self):
        chart = AccountChart()
        chart.create("Cash", OOPAccountType.ASSET)
        chart.create("Bank", OOPAccountType.ASSET)
        chart.create("Revenue", OOPAccountType.REVENUE)
        assert len(chart.by_type(OOPAccountType.ASSET)) == 2

    def test_total_assets(self):
        chart = AccountChart()
        a = chart.create("Cash", OOPAccountType.ASSET)
        a.balance = 1000.0
        assert chart.total_assets() == pytest.approx(1000.0)

    def test_total_liabilities(self):
        chart = AccountChart()
        a = chart.create("Loans", OOPAccountType.LIABILITY)
        a.balance = 500.0
        assert chart.total_liabilities() == pytest.approx(500.0)

    def test_total_equity(self):
        chart = AccountChart()
        a = chart.create("Equity", OOPAccountType.EQUITY)
        a.balance = 250.0
        assert chart.total_equity() == pytest.approx(250.0)

    def test_net_income(self):
        chart = AccountChart()
        rev = chart.create("Revenue", OOPAccountType.REVENUE)
        exp = chart.create("Expenses", OOPAccountType.EXPENSE)
        rev.balance = 800.0
        exp.balance = 300.0
        assert chart.net_income() == pytest.approx(500.0)

    def test_account_count(self):
        chart = AccountChart()
        chart.create("A", OOPAccountType.ASSET)
        chart.create("B", OOPAccountType.LIABILITY)
        assert chart.account_count == 2

    def test_all_accounts(self):
        chart = AccountChart()
        chart.create("A", OOPAccountType.ASSET)
        assert len(chart.all_accounts()) == 1

    def test_summary_keys(self):
        chart = AccountChart()
        s = chart.summary()
        for key in ("total_accounts", "assets", "liabilities", "equity", "net_income"):
            assert key in s
