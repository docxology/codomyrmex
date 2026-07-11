"""Tests for finance MCP tools.

Zero-mock tests validating the finance MCP tool wrappers.
"""

from __future__ import annotations


class TestFinanceListAccountTypes:
    """Tests for finance_list_account_types tool."""

    def test_returns_success_status(self):
        from codomyrmex.finance.mcp_tools import finance_list_account_types

        result = finance_list_account_types()
        assert result["status"] == "success"

    def test_contains_all_five_types(self):
        from codomyrmex.finance.mcp_tools import finance_list_account_types

        result = finance_list_account_types()
        types = result["account_types"]
        assert "ASSET" in types
        assert "LIABILITY" in types
        assert "EQUITY" in types
        assert "REVENUE" in types
        assert "EXPENSE" in types

    def test_returns_exactly_five_types(self):
        from codomyrmex.finance.mcp_tools import finance_list_account_types

        result = finance_list_account_types()
        assert len(result["account_types"]) == 5


class TestFinanceCreateChart:
    """Tests for finance_create_chart tool."""

    def test_create_single_account_chart(self):
        from codomyrmex.finance.mcp_tools import finance_create_chart

        result = finance_create_chart(
            accounts=[{"name": "Cash", "type": "ASSET", "code": "1000"}],
        )
        assert result["status"] == "success"
        assert result["summary"]["total_accounts"] == 1
        assert len(result["accounts"]) == 1
        assert result["accounts"][0]["name"] == "Cash"

    def test_create_multi_account_chart(self):
        from codomyrmex.finance.mcp_tools import finance_create_chart

        result = finance_create_chart(
            accounts=[
                {"name": "Cash", "type": "ASSET"},
                {"name": "Revenue", "type": "REVENUE"},
                {"name": "Rent", "type": "EXPENSE"},
            ],
        )
        assert result["status"] == "success"
        assert result["summary"]["total_accounts"] == 3

    def test_invalid_account_type_returns_error(self):
        from codomyrmex.finance.mcp_tools import finance_create_chart

        result = finance_create_chart(
            accounts=[{"name": "Bad", "type": "FAKE_TYPE"}],
        )
        assert result["status"] == "error"
        assert "message" in result


class TestFinanceRecordTransaction:
    """Tests for finance_record_transaction tool.

    The real Ledger requires 'Category:Subcategory' account name format
    and uses post_transaction with balanced entries.
    """

    def test_record_basic_transaction(self):
        from codomyrmex.finance.mcp_tools import finance_record_transaction

        result = finance_record_transaction(
            debit_account_name="Expenses:Rent",
            credit_account_name="Assets:Cash",
            amount=1000.0,
            description="Monthly rent payment",
        )
        assert result["status"] == "success"
        assert result["debit_balance"] == 1000.0
        assert result["credit_balance"] == -1000.0
        assert result["trial_balance"]["balanced"] is True

    def test_negative_amount_returns_error(self):
        from codomyrmex.finance.mcp_tools import finance_record_transaction

        result = finance_record_transaction(
            debit_account_name="Expenses:Rent",
            credit_account_name="Assets:Cash",
            amount=-100.0,
        )
        assert result["status"] == "error"
        assert "message" in result

    def test_zero_amount_transaction(self):
        from codomyrmex.finance.mcp_tools import finance_record_transaction

        result = finance_record_transaction(
            debit_account_name="Expenses:Rent",
            credit_account_name="Assets:Cash",
            amount=0.0,
        )
        assert result["status"] == "success"
        assert result["debit_balance"] == 0.0
        assert result["credit_balance"] == 0.0

    def test_invalid_account_name_format_returns_error(self):
        from codomyrmex.finance.mcp_tools import finance_record_transaction

        result = finance_record_transaction(
            debit_account_name="BadName",
            credit_account_name="AlsoBad",
            amount=100.0,
        )
        assert result["status"] == "error"
        assert "Category:Subcategory" in result["message"]
