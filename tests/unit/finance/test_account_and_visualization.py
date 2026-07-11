"""Tests for finance/account.py (Account, AccountChart) and finance/visualization.py.

Zero-mock policy: no MagicMock, no monkeypatch, no unittest.mock.
All tests exercise real code with real data.
"""

import pytest

from codomyrmex.finance.account import Account, AccountChart, AccountType
from codomyrmex.finance.visualization import (
    accounts_to_csv,
    balance_sheet_text,
    balance_table,
    group_by_type,
    income_statement_text,
)


class TestAccountCreation:
    """Test Account dataclass creation and properties."""

    def test_account_has_unique_id(self):
        a1 = Account("Cash", AccountType.ASSET)
        a2 = Account("Cash", AccountType.ASSET)
        assert a1.id != a2.id

    def test_account_starts_with_zero_balance(self):
        acct = Account("Bank", AccountType.ASSET)
        assert acct.balance == 0.0

    def test_asset_account_is_debit_normal(self):
        acct = Account("Equipment", AccountType.ASSET)
        assert acct.is_debit_normal is True

    def test_expense_account_is_debit_normal(self):
        acct = Account("Wages Expense", AccountType.EXPENSE)
        assert acct.is_debit_normal is True

    def test_liability_account_is_not_debit_normal(self):
        acct = Account("Accounts Payable", AccountType.LIABILITY)
        assert acct.is_debit_normal is False

    def test_revenue_account_is_not_debit_normal(self):
        acct = Account("Sales Revenue", AccountType.REVENUE)
        assert acct.is_debit_normal is False

    def test_equity_account_is_not_debit_normal(self):
        acct = Account("Owner Equity", AccountType.EQUITY)
        assert acct.is_debit_normal is False

    def test_account_stores_code(self):
        acct = Account("Cash", AccountType.ASSET, code="1000")
        assert acct.code == "1000"

    def test_account_repr_contains_name(self):
        acct = Account("Petty Cash", AccountType.ASSET)
        assert "Petty Cash" in repr(acct)

    def test_account_to_dict_has_required_keys(self):
        acct = Account("Revenue", AccountType.REVENUE, code="4000")
        d = acct.to_dict()
        assert "id" in d
        assert "name" in d
        assert "type" in d
        assert "balance" in d
        assert "frozen" in d
        assert d["frozen"] is False


class TestAccountDebitCredit:
    """Test debit/credit operations on accounts."""

    def test_debit_increases_asset_balance(self):
        acct = Account("Cash", AccountType.ASSET)
        acct.debit(500.0)
        assert acct.balance == 500.0

    def test_credit_decreases_asset_balance(self):
        acct = Account("Cash", AccountType.ASSET)
        acct.debit(1000.0)
        acct.credit(300.0)
        assert acct.balance == 700.0

    def test_credit_increases_liability_balance(self):
        acct = Account("Loan Payable", AccountType.LIABILITY)
        acct.credit(2000.0)
        assert acct.balance == 2000.0

    def test_debit_decreases_liability_balance(self):
        acct = Account("Loan Payable", AccountType.LIABILITY)
        acct.credit(2000.0)
        acct.debit(500.0)
        assert acct.balance == 1500.0

    def test_credit_increases_revenue_balance(self):
        acct = Account("Service Revenue", AccountType.REVENUE)
        acct.credit(1500.0)
        assert acct.balance == 1500.0

    def test_debit_increases_expense_balance(self):
        acct = Account("Rent Expense", AccountType.EXPENSE)
        acct.debit(800.0)
        assert acct.balance == 800.0

    def test_negative_debit_raises_value_error(self):
        acct = Account("Cash", AccountType.ASSET)
        with pytest.raises(ValueError, match="non-negative"):
            acct.debit(-100.0)

    def test_negative_credit_raises_value_error(self):
        acct = Account("Cash", AccountType.ASSET)
        with pytest.raises(ValueError, match="non-negative"):
            acct.credit(-50.0)

    def test_debit_on_frozen_account_raises(self):
        acct = Account("Restricted Cash", AccountType.ASSET)
        acct.freeze()
        with pytest.raises(ValueError, match="frozen"):
            acct.debit(100.0)

    def test_credit_on_frozen_account_raises(self):
        acct = Account("Old Revenue", AccountType.REVENUE)
        acct.freeze()
        with pytest.raises(ValueError, match="frozen"):
            acct.credit(100.0)

    def test_freeze_and_unfreeze_allows_operations(self):
        acct = Account("Cash", AccountType.ASSET)
        acct.freeze()
        acct.unfreeze()
        acct.debit(100.0)
        assert acct.balance == 100.0


class TestAccountChart:
    """Test AccountChart collection management."""

    def test_chart_starts_empty(self):
        chart = AccountChart()
        assert chart.account_count == 0

    def test_create_account_increments_count(self):
        chart = AccountChart()
        chart.create("Cash", AccountType.ASSET)
        assert chart.account_count == 1

    def test_create_returns_account_object(self):
        chart = AccountChart()
        acct = chart.create("Bank", AccountType.ASSET, code="1001")
        assert acct.name == "Bank"
        assert acct.account_type == AccountType.ASSET
        assert acct.code == "1001"

    def test_get_retrieves_account_by_id(self):
        chart = AccountChart()
        acct = chart.create("Cash", AccountType.ASSET)
        retrieved = chart.get(acct.id)
        assert retrieved is acct

    def test_get_returns_none_for_unknown_id(self):
        chart = AccountChart()
        assert chart.get("nonexistent-id") is None

    def test_find_by_name_locates_account(self):
        chart = AccountChart()
        chart.create("Cash", AccountType.ASSET)
        found = chart.find_by_name("Cash")
        assert found is not None
        assert found.name == "Cash"

    def test_find_by_name_returns_none_for_missing(self):
        chart = AccountChart()
        assert chart.find_by_name("Nonexistent") is None

    def test_find_by_code_locates_account(self):
        chart = AccountChart()
        chart.create("Cash", AccountType.ASSET, code="1000")
        found = chart.find_by_code("1000")
        assert found is not None
        assert found.code == "1000"

    def test_find_by_code_returns_none_for_missing(self):
        chart = AccountChart()
        assert chart.find_by_code("9999") is None

    def test_by_type_filters_correctly(self):
        chart = AccountChart()
        chart.create("Cash", AccountType.ASSET)
        chart.create("Prepaid", AccountType.ASSET)
        chart.create("Revenue", AccountType.REVENUE)
        assets = chart.by_type(AccountType.ASSET)
        assert len(assets) == 2

    def test_total_assets_sums_asset_balances(self):
        chart = AccountChart()
        cash = chart.create("Cash", AccountType.ASSET)
        equipment = chart.create("Equipment", AccountType.ASSET)
        cash.debit(1000.0)
        equipment.debit(5000.0)
        assert chart.total_assets() == 6000.0

    def test_total_liabilities_sums_liability_balances(self):
        chart = AccountChart()
        loan = chart.create("Loan", AccountType.LIABILITY)
        loan.credit(3000.0)
        assert chart.total_liabilities() == 3000.0

    def test_total_equity_sums_equity_balances(self):
        chart = AccountChart()
        equity = chart.create("Owner Equity", AccountType.EQUITY)
        equity.credit(2000.0)
        assert chart.total_equity() == 2000.0

    def test_net_income_revenue_minus_expenses(self):
        chart = AccountChart()
        rev = chart.create("Revenue", AccountType.REVENUE)
        exp = chart.create("Expenses", AccountType.EXPENSE)
        rev.credit(5000.0)
        exp.debit(2000.0)
        assert chart.net_income() == 3000.0

    def test_all_accounts_returns_all(self):
        chart = AccountChart()
        chart.create("A", AccountType.ASSET)
        chart.create("B", AccountType.LIABILITY)
        assert len(chart.all_accounts()) == 2

    def test_summary_has_correct_keys(self):
        chart = AccountChart()
        chart.create("Cash", AccountType.ASSET)
        s = chart.summary()
        assert "total_accounts" in s
        assert "assets" in s
        assert "liabilities" in s
        assert "equity" in s
        assert "net_income" in s
        assert s["total_accounts"] == 1


class TestFinanceVisualization:
    """Test visualization functions from finance/visualization.py."""

    def _make_ledger_accounts(self):
        """Build a small set of Account objects via AccountChart for viz tests."""
        import uuid
        from decimal import Decimal

        from codomyrmex.finance.ledger.ledger import Account as LedgerAccount
        from codomyrmex.finance.ledger.ledger import AccountType as LedgerAccountType

        # Create ledger Account objects (visualization uses ledger.Account)
        cash = LedgerAccount(
            id=str(uuid.uuid4()),
            name="Assets:Cash",
            account_type=LedgerAccountType.ASSET,
            balance=Decimal("1000.00"),
        )
        revenue = LedgerAccount(
            id=str(uuid.uuid4()),
            name="Revenue:Sales",
            account_type=LedgerAccountType.REVENUE,
            balance=Decimal("500.00"),
        )
        expense = LedgerAccount(
            id=str(uuid.uuid4()),
            name="Expenses:Rent",
            account_type=LedgerAccountType.EXPENSE,
            balance=Decimal("200.00"),
        )
        liability = LedgerAccount(
            id=str(uuid.uuid4()),
            name="Liabilities:Loan",
            account_type=LedgerAccountType.LIABILITY,
            balance=Decimal("300.00"),
        )
        equity = LedgerAccount(
            id=str(uuid.uuid4()),
            name="Equity:Owner",
            account_type=LedgerAccountType.EQUITY,
            balance=Decimal("700.00"),
        )
        return [cash, revenue, expense, liability, equity]

    def test_balance_table_with_empty_list(self):
        result = balance_table([])
        assert result == "No accounts."

    def test_balance_table_contains_header(self):
        accounts = self._make_ledger_accounts()
        result = balance_table(accounts)
        assert "Account" in result
        assert "Balance" in result

    def test_balance_table_contains_account_names(self):
        accounts = self._make_ledger_accounts()
        result = balance_table(accounts)
        assert "Assets:Cash" in result
        assert "Revenue:Sales" in result

    def test_group_by_type_separates_types(self):
        accounts = self._make_ledger_accounts()
        groups = group_by_type(accounts)
        assert "asset" in groups
        assert "revenue" in groups
        assert len(groups["asset"]) == 1

    def test_income_statement_text_contains_income_statement_header(self):
        accounts = self._make_ledger_accounts()
        result = income_statement_text(accounts)
        assert "INCOME STATEMENT" in result

    def test_income_statement_text_contains_revenue_and_expense(self):
        accounts = self._make_ledger_accounts()
        result = income_statement_text(accounts)
        assert "Revenue" in result
        assert "Expenses" in result
        assert "NET INCOME" in result

    def test_balance_sheet_text_has_correct_sections(self):
        accounts = self._make_ledger_accounts()
        result = balance_sheet_text(accounts)
        assert "BALANCE SHEET" in result
        assert "ASSETS:" in result
        assert "LIABILITIES:" in result
        assert "EQUITY:" in result

    def test_accounts_to_csv_has_header_row(self):
        accounts = self._make_ledger_accounts()
        result = accounts_to_csv(accounts)
        first_line = result.split("\n")[0]
        assert "name" in first_line
        assert "balance" in first_line

    def test_accounts_to_csv_has_one_row_per_account(self):
        accounts = self._make_ledger_accounts()
        result = accounts_to_csv(accounts)
        # header + 5 accounts
        lines = result.strip().split("\n")
        assert len(lines) == 6
