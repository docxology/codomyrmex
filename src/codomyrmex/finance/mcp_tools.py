"""MCP tool definitions for the finance module.

Exposes ledger operations and account management as MCP tools.
Uses lazy imports from account and ledger submodules directly
to avoid broken top-level imports (forecasting/payroll/taxes missing).
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_account_types():
    """Lazy import of AccountType enum."""
    from codomyrmex.finance.account import AccountType

    return AccountType


def _get_account_chart():
    """Lazy import of AccountChart class."""
    from codomyrmex.finance.account import AccountChart

    return AccountChart


@mcp_tool(
    category="finance",
    description="list available account types for double-entry bookkeeping.",
)
def finance_list_account_types() -> dict[str, Any]:
    """list all supported financial account types.

    Returns:
        dict with keys: status, account_types
    """
    try:
        account_type = _get_account_types()
        return {
            "status": "success",
            "account_types": [at.name for at in account_type],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="finance",
    description=(
        "Create an account chart with specified accounts and return a financial summary "
        "including total assets, liabilities, equity, and net income."
    ),
)
def finance_create_chart(
    accounts: list[dict[str, str]],
) -> dict[str, Any]:
    """Create an account chart and return its summary.

    Args:
        accounts: list of account dicts with keys 'name', 'type', and optional 'code'.
                  Type must be one of: ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE.

    Returns:
        dict with keys: status, summary, accounts
    """
    try:
        account_type_cls = _get_account_types()
        chart_cls = _get_account_chart()
        chart = chart_cls()

        created = []
        for acct_spec in accounts:
            name = acct_spec["name"]
            type_name = acct_spec["type"].upper()
            code = acct_spec.get("code", "")
            at = account_type_cls[type_name]
            acct = chart.create(name, at, code=code)
            created.append(acct.to_dict())

        return {
            "status": "success",
            "summary": chart.summary(),
            "accounts": created,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="finance",
    description=(
        "Record a double-entry transaction in a ledger between two accounts "
        "and return updated balances."
    ),
)
def finance_record_transaction(
    debit_account_name: str,
    credit_account_name: str,
    amount: float,
    description: str = "",
) -> dict[str, Any]:
    """Record a double-entry transaction and return the resulting balances.

    Creates a temporary ledger with two accounts (Expense and Asset),
    posts a balanced transaction, and returns the balances.
    Account names must follow 'Category:Subcategory' format.

    Args:
        debit_account_name: Name of the expense account to debit
                            (format: 'Category:Subcategory').
        credit_account_name: Name of the asset account to credit
                             (format: 'Category:Subcategory').
        amount: Transaction amount (must be non-negative).
        description: Human-readable transaction description.

    Returns:
        dict with keys: status, debit_balance, credit_balance, trial_balance
    """
    try:
        from codomyrmex.finance.ledger import AccountType, Ledger

        if amount < 0:
            return {"status": "error", "message": "Amount must be non-negative."}

        ledger = Ledger("MCP Transaction Ledger")
        debit_acct = ledger.create_account(debit_account_name, AccountType.EXPENSE)
        credit_acct = ledger.create_account(credit_account_name, AccountType.ASSET)

        ledger.post_transaction(
            entries=[
                {"account_id": debit_acct.id, "amount": amount},
                {"account_id": credit_acct.id, "amount": -amount},
            ],
            description=description,
        )

        trial = ledger.trial_balance()

        return {
            "status": "success",
            "debit_balance": float(ledger.get_balance(debit_acct.id)),
            "credit_balance": float(ledger.get_balance(credit_acct.id)),
            "trial_balance": trial,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
