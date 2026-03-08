"""Tests for finance.account and finance.ledger (top-level modules)."""

import pytest
from decimal import Decimal

from codomyrmex.finance.account import Account, AccountChart, AccountType
from codomyrmex.finance.ledger import Ledger, LedgerError, Transaction, TransactionEntry
from codomyrmex.finance.ledger.ledger import AccountType as LedgerAccountType


class TestAccountType:
    def test_five_types(self):
        types = {t for t in AccountType}
        assert len(types) == 5

    def test_has_asset(self):
        assert AccountType.ASSET is not None

    def test_has_liability(self):
        assert AccountType.LIABILITY is not None

    def test_has_equity(self):
        assert AccountType.EQUITY is not None

    def test_has_revenue(self):
        assert AccountType.REVENUE is not None

    def test_has_expense(self):
        assert AccountType.EXPENSE is not None


class TestAccount:
    def test_construction(self):
        acc = Account("Cash", AccountType.ASSET)
        assert acc.name == "Cash"
        assert acc.account_type == AccountType.ASSET
        assert acc.balance == 0.0

    def test_id_auto_generated(self):
        acc = Account("Cash", AccountType.ASSET)
        assert len(acc.id) > 0

    def test_is_debit_normal_asset(self):
        acc = Account("Cash", AccountType.ASSET)
        assert acc.is_debit_normal is True

    def test_is_debit_normal_expense(self):
        acc = Account("Rent", AccountType.EXPENSE)
        assert acc.is_debit_normal is True

    def test_is_not_debit_normal_liability(self):
        acc = Account("Loan", AccountType.LIABILITY)
        assert acc.is_debit_normal is False

    def test_is_not_debit_normal_revenue(self):
        acc = Account("Sales", AccountType.REVENUE)
        assert acc.is_debit_normal is False

    def test_debit_increases_asset(self):
        acc = Account("Cash", AccountType.ASSET)
        acc.debit(100.0)
        assert acc.balance == 100.0

    def test_credit_decreases_asset(self):
        acc = Account("Cash", AccountType.ASSET)
        acc.debit(200.0)
        acc.credit(50.0)
        assert acc.balance == 150.0

    def test_credit_increases_liability(self):
        acc = Account("Loan", AccountType.LIABILITY)
        acc.credit(500.0)
        assert acc.balance == 500.0

    def test_debit_decreases_liability(self):
        acc = Account("Loan", AccountType.LIABILITY)
        acc.credit(500.0)
        acc.debit(100.0)
        assert acc.balance == 400.0

    def test_credit_increases_revenue(self):
        acc = Account("Sales", AccountType.REVENUE)
        acc.credit(300.0)
        assert acc.balance == 300.0

    def test_debit_negative_raises(self):
        acc = Account("Cash", AccountType.ASSET)
        with pytest.raises(ValueError):
            acc.debit(-10.0)

    def test_credit_negative_raises(self):
        acc = Account("Cash", AccountType.ASSET)
        with pytest.raises(ValueError):
            acc.credit(-5.0)

    def test_freeze_blocks_debit(self):
        acc = Account("Cash", AccountType.ASSET)
        acc.freeze()
        with pytest.raises(ValueError, match="frozen"):
            acc.debit(100.0)

    def test_freeze_blocks_credit(self):
        acc = Account("Sales", AccountType.REVENUE)
        acc.freeze()
        with pytest.raises(ValueError, match="frozen"):
            acc.credit(50.0)

    def test_unfreeze_allows_operations(self):
        acc = Account("Cash", AccountType.ASSET)
        acc.freeze()
        acc.unfreeze()
        acc.debit(10.0)  # Should not raise
        assert acc.balance == 10.0

    def test_to_dict_fields(self):
        acc = Account("Bank", AccountType.ASSET, code="1010")
        d = acc.to_dict()
        assert d["name"] == "Bank"
        assert d["code"] == "1010"
        assert d["type"] == "ASSET"
        assert d["balance"] == 0.0
        assert d["frozen"] is False

    def test_repr_contains_name(self):
        acc = Account("Cash", AccountType.ASSET)
        assert "Cash" in repr(acc)


class TestAccountChart:
    def test_empty_chart(self):
        chart = AccountChart()
        assert chart.account_count == 0

    def test_create_account(self):
        chart = AccountChart()
        acc = chart.create("Cash", AccountType.ASSET)
        assert acc.name == "Cash"
        assert chart.account_count == 1

    def test_get_by_id(self):
        chart = AccountChart()
        acc = chart.create("Cash", AccountType.ASSET)
        retrieved = chart.get(acc.id)
        assert retrieved is acc

    def test_get_nonexistent_returns_none(self):
        chart = AccountChart()
        assert chart.get("nonexistent-id") is None

    def test_find_by_name(self):
        chart = AccountChart()
        chart.create("Cash", AccountType.ASSET)
        found = chart.find_by_name("Cash")
        assert found is not None
        assert found.name == "Cash"

    def test_find_by_name_missing_returns_none(self):
        chart = AccountChart()
        assert chart.find_by_name("Missing") is None

    def test_find_by_code(self):
        chart = AccountChart()
        chart.create("Bank", AccountType.ASSET, code="1010")
        found = chart.find_by_code("1010")
        assert found is not None

    def test_find_by_code_missing_returns_none(self):
        chart = AccountChart()
        assert chart.find_by_code("9999") is None

    def test_by_type(self):
        chart = AccountChart()
        chart.create("Cash", AccountType.ASSET)
        chart.create("Inventory", AccountType.ASSET)
        chart.create("Revenue", AccountType.REVENUE)
        assets = chart.by_type(AccountType.ASSET)
        assert len(assets) == 2

    def test_total_assets(self):
        chart = AccountChart()
        cash = chart.create("Cash", AccountType.ASSET)
        cash.debit(1000.0)
        assert chart.total_assets() == 1000.0

    def test_total_liabilities(self):
        chart = AccountChart()
        loan = chart.create("Loan", AccountType.LIABILITY)
        loan.credit(500.0)
        assert chart.total_liabilities() == 500.0

    def test_net_income(self):
        chart = AccountChart()
        rev = chart.create("Revenue", AccountType.REVENUE)
        exp = chart.create("Rent", AccountType.EXPENSE)
        rev.credit(1000.0)
        exp.debit(300.0)
        assert abs(chart.net_income() - 700.0) < 1e-9

    def test_summary_keys(self):
        chart = AccountChart()
        s = chart.summary()
        assert "total_accounts" in s
        assert "assets" in s
        assert "liabilities" in s
        assert "equity" in s
        assert "net_income" in s

    def test_all_accounts(self):
        chart = AccountChart()
        chart.create("A", AccountType.ASSET)
        chart.create("B", AccountType.LIABILITY)
        accounts = chart.all_accounts()
        assert len(accounts) == 2


class TestTransactionEntry:
    def test_construction(self):
        e = TransactionEntry(account_id="acc-1", amount=Decimal("100.00"))
        assert e.account_id == "acc-1"
        assert e.amount == Decimal("100.00")

    def test_with_description(self):
        e = TransactionEntry(account_id="a", amount=Decimal("-50.00"), description="Credit leg")
        assert e.description == "Credit leg"

    def test_default_description_empty(self):
        e = TransactionEntry(account_id="a", amount=Decimal("1.00"))
        assert e.description == ""


class TestTransaction:
    def _make_balanced(self) -> Transaction:
        entries = [
            TransactionEntry(account_id="a1", amount=Decimal("100.00")),
            TransactionEntry(account_id="a2", amount=Decimal("-100.00")),
        ]
        return Transaction(id="txn-1", entries=entries, description="Sale")

    def test_construction(self):
        txn = self._make_balanced()
        assert txn.id == "txn-1"
        assert txn.description == "Sale"
        assert len(txn.entries) == 2

    def test_is_balanced_true(self):
        txn = self._make_balanced()
        assert txn.is_balanced is True

    def test_is_balanced_false(self):
        entries = [TransactionEntry(account_id="a1", amount=Decimal("50.00"))]
        txn = Transaction(id="t2", entries=entries, description="unbalanced")
        assert txn.is_balanced is False

    def test_is_balanced_multi_entry(self):
        entries = [
            TransactionEntry(account_id="a1", amount=Decimal("300.00")),
            TransactionEntry(account_id="a2", amount=Decimal("-200.00")),
            TransactionEntry(account_id="a3", amount=Decimal("-100.00")),
        ]
        txn = Transaction(id="t3", entries=entries, description="split")
        assert txn.is_balanced is True

    def test_timestamp_set(self):
        txn = self._make_balanced()
        assert txn.timestamp is not None


class TestLedger:
    def _make_ledger(self):
        ledger = Ledger("Test Books")
        cash = ledger.create_account("Assets:Cash", LedgerAccountType.ASSET)
        revenue = ledger.create_account("Revenue:Sales", LedgerAccountType.REVENUE)
        return ledger, cash, revenue

    def test_create_account(self):
        ledger = Ledger()
        acc = ledger.create_account("Assets:Cash", LedgerAccountType.ASSET)
        assert acc.name == "Assets:Cash"

    def test_create_account_returns_account(self):
        ledger = Ledger()
        acc = ledger.create_account("Assets:Bank", LedgerAccountType.ASSET)
        assert acc.account_type == LedgerAccountType.ASSET

    def test_duplicate_account_raises(self):
        ledger = Ledger()
        ledger.create_account("Assets:Cash", LedgerAccountType.ASSET)
        with pytest.raises(LedgerError, match="already exists"):
            ledger.create_account("Assets:Cash", LedgerAccountType.ASSET)

    def test_invalid_account_name_raises(self):
        ledger = Ledger()
        with pytest.raises(LedgerError):
            ledger.create_account("Cash", LedgerAccountType.ASSET)

    def test_post_transaction_updates_balances(self):
        ledger, cash, revenue = self._make_ledger()
        ledger.post_transaction(
            [
                {"account_id": cash.id, "amount": 500},
                {"account_id": revenue.id, "amount": -500},
            ],
            description="Sale proceeds",
        )
        assert ledger.get_balance(cash.id) == Decimal("500.00")
        assert ledger.get_balance(revenue.id) == Decimal("500.00")

    def test_post_transaction_unbalanced_raises(self):
        ledger, cash, revenue = self._make_ledger()
        with pytest.raises(LedgerError, match="balance"):
            ledger.post_transaction(
                [{"account_id": cash.id, "amount": 100}],
                description="Unbalanced",
            )

    def test_post_transaction_empty_raises(self):
        ledger = Ledger()
        with pytest.raises(LedgerError):
            ledger.post_transaction([], description="Empty")

    def test_post_transaction_unknown_account_raises(self):
        ledger = Ledger()
        with pytest.raises(LedgerError):
            ledger.post_transaction(
                [
                    {"account_id": "nope-1", "amount": 100},
                    {"account_id": "nope-2", "amount": -100},
                ],
                description="Bad accounts",
            )

    def test_get_balance_unknown_raises(self):
        ledger = Ledger()
        with pytest.raises(LedgerError):
            ledger.get_balance("nonexistent-id")

    def test_trial_balance_balanced_after_transaction(self):
        ledger, cash, revenue = self._make_ledger()
        ledger.post_transaction(
            [
                {"account_id": cash.id, "amount": 200},
                {"account_id": revenue.id, "amount": -200},
            ],
            description="Sale",
        )
        tb = ledger.trial_balance()
        assert tb["balanced"] is True

    def test_trial_balance_empty_ledger(self):
        ledger = Ledger()
        tb = ledger.trial_balance()
        assert tb["balanced"] is True

    def test_trial_balance_has_keys(self):
        ledger = Ledger()
        tb = ledger.trial_balance()
        assert "balances" in tb
        assert "total_debits" in tb
        assert "total_credits" in tb

    def test_get_balance_sheet_keys(self):
        ledger, cash, revenue = self._make_ledger()
        bs = ledger.get_balance_sheet()
        assert "assets" in bs
        assert "liabilities" in bs
        assert "equity" in bs
        assert "balanced" in bs

    def test_get_income_statement_keys(self):
        ledger, cash, revenue = self._make_ledger()
        ledger.post_transaction(
            [
                {"account_id": cash.id, "amount": 1000},
                {"account_id": revenue.id, "amount": -1000},
            ],
            description="Revenue",
        )
        stmt = ledger.get_income_statement()
        assert "revenue" in stmt
        assert "expenses" in stmt
        assert "net_income" in stmt

    def test_repr_contains_name(self):
        ledger = Ledger("My Books")
        assert "My Books" in repr(ledger)

    def test_ledger_default_name(self):
        ledger = Ledger()
        assert "General Ledger" in repr(ledger)


class TestValidationSchemas:
    """Tests for validation.schemas (Result and ResultStatus)."""

    def test_import(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        assert Result is not None
        assert ResultStatus is not None

    def test_result_status_has_success(self):
        from codomyrmex.validation.schemas import ResultStatus
        assert ResultStatus.SUCCESS.value == "success"

    def test_result_status_has_failure(self):
        from codomyrmex.validation.schemas import ResultStatus
        assert ResultStatus.FAILURE.value == "failure"

    def test_result_status_has_skipped(self):
        from codomyrmex.validation.schemas import ResultStatus
        assert ResultStatus.SKIPPED.value == "skipped"

    def test_result_ok_when_success(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        r = Result(status=ResultStatus.SUCCESS)
        assert r.ok is True

    def test_result_not_ok_when_failure(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        r = Result(status=ResultStatus.FAILURE, message="Something failed")
        assert r.ok is False

    def test_result_not_ok_when_partial(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        r = Result(status=ResultStatus.PARTIAL)
        assert r.ok is False

    def test_result_with_data(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        r = Result(status=ResultStatus.SUCCESS, data={"key": "value"})
        assert r.data == {"key": "value"}

    def test_result_with_errors(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        r = Result(status=ResultStatus.FAILURE, errors=["err1", "err2"])
        assert len(r.errors) == 2

    def test_result_independent_default_errors(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        r1 = Result(status=ResultStatus.SUCCESS)
        r2 = Result(status=ResultStatus.SUCCESS)
        r1.errors.append("x")
        assert r2.errors == []

    def test_result_to_dict(self):
        from codomyrmex.validation.schemas import Result, ResultStatus
        r = Result(status=ResultStatus.SUCCESS, message="ok")
        d = r.to_dict()
        assert d["status"] == "success"
        assert d["message"] == "ok"
