"""Double-entry bookkeeping ledger with balance sheet and income statement support.

Provides a full general ledger implementation following standard accounting
principles: every transaction must balance (total debits == total credits),
accounts are classified by type, and financial statements can be generated
from the recorded data.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class AccountType(Enum):
    """Standard account classifications in double-entry bookkeeping."""

    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class LedgerError(Exception):
    """Raised when a ledger operation fails validation."""


@dataclass
class Account:
    """A named financial account with a type and running balance.

    Attributes:
        id: Unique identifier for the account.
        name: Human-readable account name (format "Category:Subcategory").
        account_type: Classification that governs debit/credit behaviour.
        balance: Current balance (interpretation depends on type).
        code: Optional account code for reporting.
        frozen: If True, no further transactions can be posted.
        created_at: Timestamp when the account was created.
    """

    id: str
    name: str
    account_type: AccountType
    balance: Decimal = field(default_factory=lambda: Decimal("0.00"))
    code: str = ""
    frozen: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate account name format."""
        if ":" not in self.name:
            raise LedgerError(
                f"Account name '{self.name}' must follow 'Category:Subcategory' format."
            )

    @property
    def is_debit_normal(self) -> bool:
        """True if this account increases with debits."""
        return self.account_type in (AccountType.ASSET, AccountType.EXPENSE)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "type": self.account_type.value,
            "balance": float(self.balance),
            "frozen": self.frozen,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Account(id={self.id!r}, name={self.name!r}, "
            f"type={self.account_type.value}, balance={self.balance})"
        )


@dataclass
class TransactionEntry:
    """A single leg of a transaction affecting one account.

    Positive ``amount`` is a debit; negative ``amount`` is a credit.
    """

    account_id: str
    amount: Decimal
    description: str = ""


@dataclass
class Transaction:
    """An atomic collection of balanced entries.

    The sum of all entry amounts must equal zero (debits == credits).
    """

    id: str
    entries: list[TransactionEntry]
    description: str
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_balanced(self) -> bool:
        """Return True when total debits equal total credits."""
        return sum(e.amount for e in self.entries) == Decimal("0.00")


class Ledger:
    """Double-entry bookkeeping ledger.

    Usage::

        ledger = Ledger("My Company")
        cash = ledger.create_account("Cash", AccountType.ASSET)
        revenue = ledger.create_account("Sales Revenue", AccountType.REVENUE)
        ledger.post_transaction(
            [{"account_id": cash.id, "amount": 1000},
             {"account_id": revenue.id, "amount": -1000}],
            description="Sold goods for cash",
        )
        print(ledger.get_balance(cash.id))  # 1000.0
    """

    def __init__(self, name: str = "General Ledger") -> None:
        self.name = name
        self.accounts: dict[str, Account] = {}
        self.transactions: list[Transaction] = []

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    def create_account(
        self, name: str, account_type: AccountType, code: str = ""
    ) -> Account:
        """Create and register a new account.

        Args:
            name: Display name for the account (must be "Category:Subcategory").
            account_type: One of the five standard account types.
            code: Optional account code.

        Returns:
            The newly created :class:`Account`.

        Raises:
            LedgerError: If name format is invalid or account already exists.
        """
        for acct in self.accounts.values():
            if acct.name == name:
                raise LedgerError(f"Account with name '{name}' already exists.")

        account_id = str(uuid.uuid4())
        account = Account(
            id=account_id,
            name=name,
            account_type=account_type,
            code=code,
        )
        self.accounts[account_id] = account
        logger.info("Created account %s (%s)", name, account_type.value)
        return account

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def post_transaction(
        self,
        entries: list[dict],
        description: str,
    ) -> Transaction:
        """Post a balanced transaction to the ledger.

        Each entry dict must contain ``account_id`` (str) and ``amount``.
        Positive amounts are debits, negative amounts are credits.
        An optional ``description`` key is forwarded to the entry.

        Args:
            entries: List of entry dicts.
            description: Human-readable description of the transaction.

        Returns:
            The recorded :class:`Transaction`.

        Raises:
            LedgerError: If the entries do not balance or reference unknown
                accounts.
        """
        if not entries:
            raise LedgerError("A transaction must have at least one entry.")

        # Validate accounts exist
        for entry_dict in entries:
            aid = entry_dict.get("account_id")
            if aid not in self.accounts:
                raise LedgerError(f"Account '{aid}' not found in the ledger.")

        # Build TransactionEntry objects
        tx_entries: list[TransactionEntry] = []
        for entry_dict in entries:
            amount = Decimal(str(entry_dict["amount"])).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_EVEN
            )
            tx_entries.append(
                TransactionEntry(
                    account_id=entry_dict["account_id"],
                    amount=amount,
                    description=entry_dict.get("description", ""),
                )
            )

        # Balance check
        total = sum(e.amount for e in tx_entries)
        if total != Decimal("0.00"):
            raise LedgerError(
                f"Transaction does not balance: net amount is {total} (must be 0)."
            )

        txn = Transaction(
            id=str(uuid.uuid4()),
            entries=tx_entries,
            description=description,
        )

        # Apply to account balances using normal-balance rules
        for entry in tx_entries:
            acct = self.accounts[entry.account_id]
            if acct.frozen:
                raise LedgerError(f"Account '{acct.name}' is frozen.")

            if acct.is_debit_normal:
                acct.balance += entry.amount
            else:
                acct.balance -= entry.amount

        self.transactions.append(txn)
        logger.info("Posted transaction %s: %s", txn.id[:8], description)
        return txn

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_balance(self, account_id: str) -> Decimal:
        """Return the current balance of the given account.

        Raises:
            LedgerError: If the account does not exist.
        """
        if account_id not in self.accounts:
            raise LedgerError(f"Account '{account_id}' not found.")
        return self.accounts[account_id].balance

    def get_balance_sheet(self) -> dict:
        """Generate a balance sheet summary.

        Returns a dict with keys ``assets``, ``liabilities``, ``equity``,
        each mapping account names to their balances, plus ``total_assets``,
        ``total_liabilities``, ``total_equity``, and a boolean
        ``balanced`` flag.
        """
        assets: dict[str, Decimal] = {}
        liabilities: dict[str, Decimal] = {}
        equity: dict[str, Decimal] = {}

        for acct in self.accounts.values():
            if acct.account_type == AccountType.ASSET:
                assets[acct.name] = acct.balance
            elif acct.account_type == AccountType.LIABILITY:
                liabilities[acct.name] = acct.balance
            elif acct.account_type == AccountType.EQUITY:
                equity[acct.name] = acct.balance

        total_a = sum(assets.values(), Decimal("0.00"))
        total_l = sum(liabilities.values(), Decimal("0.00"))
        total_e = sum(equity.values(), Decimal("0.00"))

        return {
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "total_assets": total_a,
            "total_liabilities": total_l,
            "total_equity": total_e,
            "balanced": total_a == (total_l + total_e),
        }

    def get_income_statement(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dict:
        """Generate an income statement (profit & loss) for a date range.

        If *start* or *end* is ``None`` they default to the minimum or
        maximum possible range respectively.

        Returns a dict with ``revenue``, ``expenses``, ``total_revenue``,
        ``total_expenses``, and ``net_income``.
        """
        revenue: dict[str, Decimal] = {}
        expenses: dict[str, Decimal] = {}

        # Filter transactions by date range
        filtered_txns = self.transactions
        if start is not None:
            filtered_txns = [t for t in filtered_txns if t.timestamp >= start]
        if end is not None:
            filtered_txns = [t for t in filtered_txns if t.timestamp <= end]

        # Accumulate entry amounts for revenue/expense accounts
        for txn in filtered_txns:
            for entry in txn.entries:
                acct = self.accounts.get(entry.account_id)
                if acct is None:
                    continue
                if acct.account_type == AccountType.REVENUE:
                    revenue[acct.name] = revenue.get(acct.name, Decimal("0.00")) + abs(
                        entry.amount
                    )
                elif acct.account_type == AccountType.EXPENSE:
                    expenses[acct.name] = expenses.get(
                        acct.name, Decimal("0.00")
                    ) + abs(entry.amount)

        total_rev = sum(revenue.values(), Decimal("0.00"))
        total_exp = sum(expenses.values(), Decimal("0.00"))

        return {
            "revenue": revenue,
            "expenses": expenses,
            "total_revenue": total_rev,
            "total_expenses": total_exp,
            "net_income": total_rev - total_exp,
        }

    def trial_balance(self) -> dict:
        """Compute the trial balance for the ledger.

        Returns a dict mapping account names to their balances and includes
        ``total_debits``, ``total_credits``, and a ``balanced`` flag.
        """
        balances: dict[str, Decimal] = {}
        total_debits = Decimal("0.00")
        total_credits = Decimal("0.00")

        for acct in self.accounts.values():
            balances[acct.name] = acct.balance
            normal_debit = acct.account_type in (AccountType.ASSET, AccountType.EXPENSE)
            if normal_debit:
                total_debits += acct.balance
            else:
                total_credits += acct.balance

        return {
            "balances": balances,
            "total_debits": total_debits,
            "total_credits": total_credits,
            "balanced": total_debits == total_credits,
        }

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Ledger(name={self.name!r}, accounts={len(self.accounts)}, "
            f"transactions={len(self.transactions)})"
        )
