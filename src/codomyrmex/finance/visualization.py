"""Financial data visualization — account balances, transaction trends, and reports.

Provides:
- balance_table: formatted text table of account balances
- transaction_summary: grouped transaction statistics
- income_statement_text: simple income statement report
- balance_sheet_text: simplified balance sheet
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .account import Account, AccountType


def balance_table(accounts: list[Account]) -> str:
    """Generate a text table of account balances.

    Args:
        accounts: List of Account objects.

    Returns:
        Formatted multi-line table string.
    """
    if not accounts:
        return "No accounts."
    lines = [f"{'Account':<30} {'Type':<12} {'Balance':>12}"]
    lines.append("-" * 56)
    for acct in sorted(accounts, key=lambda a: a.account_type.name):
        lines.append(f"{acct.name:<30} {acct.account_type.name:<12} {acct.balance:>12,.2f}")
    total = sum(a.balance for a in accounts)
    lines.append("-" * 56)
    lines.append(f"{'TOTAL':<30} {'':12} {total:>12,.2f}")
    return "\n".join(lines)


def group_by_type(accounts: list[Account]) -> dict[str, list[Account]]:
    """Group accounts by their AccountType."""
    groups: dict[str, list[Account]] = defaultdict(list)
    for acct in accounts:
        groups[acct.account_type.name].append(acct)
    return dict(groups)


def income_statement_text(accounts: list[Account]) -> str:
    """Generate a simple text income statement.

    Revenue minus Expenses = Net Income.
    """
    revenue_accts = [a for a in accounts if a.account_type == AccountType.REVENUE]
    expense_accts = [a for a in accounts if a.account_type == AccountType.EXPENSE]

    lines = ["INCOME STATEMENT", "=" * 40]
    lines.append("Revenue:")
    total_rev = 0.0
    for acct in revenue_accts:
        lines.append(f"  {acct.name:<28} {acct.balance:>10,.2f}")
        total_rev += acct.balance
    lines.append(f"  {'Total Revenue':<28} {total_rev:>10,.2f}")

    lines.append("")
    lines.append("Expenses:")
    total_exp = 0.0
    for acct in expense_accts:
        lines.append(f"  {acct.name:<28} {acct.balance:>10,.2f}")
        total_exp += acct.balance
    lines.append(f"  {'Total Expenses':<28} {total_exp:>10,.2f}")

    lines.append("-" * 40)
    net = total_rev - total_exp
    lines.append(f"  {'NET INCOME':<28} {net:>10,.2f}")
    return "\n".join(lines)


def balance_sheet_text(accounts: list[Account]) -> str:
    """Generate a simplified balance sheet.

    Assets = Liabilities + Equity.
    """
    assets = [a for a in accounts if a.account_type == AccountType.ASSET]
    liabilities = [a for a in accounts if a.account_type == AccountType.LIABILITY]
    equity = [a for a in accounts if a.account_type == AccountType.EQUITY]

    lines = ["BALANCE SHEET", "=" * 40]

    lines.append("ASSETS:")
    total_a = 0.0
    for acct in assets:
        lines.append(f"  {acct.name:<28} {acct.balance:>10,.2f}")
        total_a += acct.balance
    lines.append(f"  {'Total Assets':<28} {total_a:>10,.2f}")

    lines.append("")
    lines.append("LIABILITIES:")
    total_l = 0.0
    for acct in liabilities:
        lines.append(f"  {acct.name:<28} {acct.balance:>10,.2f}")
        total_l += acct.balance
    lines.append(f"  {'Total Liabilities':<28} {total_l:>10,.2f}")

    lines.append("")
    lines.append("EQUITY:")
    total_e = 0.0
    for acct in equity:
        lines.append(f"  {acct.name:<28} {acct.balance:>10,.2f}")
        total_e += acct.balance
    lines.append(f"  {'Total Equity':<28} {total_e:>10,.2f}")

    lines.append("-" * 40)
    lines.append(f"  {'L + E':<28} {total_l + total_e:>10,.2f}")
    balanced = abs(total_a - (total_l + total_e)) < 0.01
    lines.append(f"  Balanced: {'✅' if balanced else '❌'}")
    return "\n".join(lines)


def accounts_to_csv(accounts: list[Account]) -> str:
    """Export accounts as CSV."""
    lines = ["name,type,code,balance"]
    for acct in accounts:
        lines.append(f'"{acct.name}","{acct.account_type.name}","{acct.code}",{acct.balance:.2f}')
    return "\n".join(lines)
