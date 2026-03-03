"""Financial account management with double-entry support.

Provides:
- AccountType: enum for the 5 fundamental account types
- Account: named ledger account with balance, debit/credit operations
- AccountChart: collection of accounts with lookup and reporting
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any
from uuid import uuid4


class AccountType(Enum):
    """Primary account types in double-entry bookkeeping."""
    ASSET = auto()
    LIABILITY = auto()
    EQUITY = auto()
    REVENUE = auto()
    EXPENSE = auto()


class Account:
    """A financial account with debit/credit operations.

    Normal balance direction follows accounting conventions:
    - Assets/Expenses: debit-normal (debit increases balance)
    - Liabilities/Equity/Revenue: credit-normal (credit increases balance)
    """

    def __init__(self, name: str, account_type: AccountType, code: str = "") -> None:
        """Initialize this instance."""
        self.id: str = str(uuid4())
        self.name = name
        self.account_type = account_type
        self.code = code
        self.balance: float = 0.0
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self._frozen: bool = False

    @property
    def is_debit_normal(self) -> bool:
        """True if this account increases with debits."""
        return self.account_type in (AccountType.ASSET, AccountType.EXPENSE)

    def debit(self, amount: float) -> None:
        """Record a debit to this account."""
        if self._frozen:
            raise ValueError(f"Account '{self.name}' is frozen")
        if amount < 0:
            raise ValueError("Debit amount must be non-negative")
        if self.is_debit_normal:
            self.balance += amount
        else:
            self.balance -= amount

    def credit(self, amount: float) -> None:
        """Record a credit to this account."""
        if self._frozen:
            raise ValueError(f"Account '{self.name}' is frozen")
        if amount < 0:
            raise ValueError("Credit amount must be non-negative")
        if self.is_debit_normal:
            self.balance -= amount
        else:
            self.balance += amount

    def freeze(self) -> None:
        """Freeze this account (no further debits/credits)."""
        self._frozen = True

    def unfreeze(self) -> None:
        """unfreeze ."""
        self._frozen = False

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "type": self.account_type.name,
            "balance": self.balance,
            "frozen": self._frozen,
        }

    def __repr__(self) -> str:
        """repr ."""
        return f"Account(name='{self.name}', type={self.account_type.name}, balance={self.balance:.2f})"


class AccountChart:
    """Chart of accounts — organized collection of financial accounts.

    Example::

        chart = AccountChart()
        cash = chart.create("Cash", AccountType.ASSET, code="1000")
        revenue = chart.create("Sales Revenue", AccountType.REVENUE, code="4000")
        print(chart.total_assets())
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._accounts: dict[str, Account] = {}

    def create(self, name: str, account_type: AccountType, code: str = "") -> Account:
        """Create and register a new account."""
        acct = Account(name, account_type, code=code)
        self._accounts[acct.id] = acct
        return acct

    def get(self, account_id: str) -> Account | None:
        """Return the requested value."""
        return self._accounts.get(account_id)

    def find_by_name(self, name: str) -> Account | None:
        """find By Name ."""
        for acct in self._accounts.values():
            if acct.name == name:
                return acct
        return None

    def find_by_code(self, code: str) -> Account | None:
        """find By Code ."""
        for acct in self._accounts.values():
            if acct.code == code:
                return acct
        return None

    def by_type(self, account_type: AccountType) -> list[Account]:
        """by Type ."""
        return [a for a in self._accounts.values() if a.account_type == account_type]

    def total_assets(self) -> float:
        """total Assets ."""
        return sum(a.balance for a in self.by_type(AccountType.ASSET))

    def total_liabilities(self) -> float:
        """total Liabilities ."""
        return sum(a.balance for a in self.by_type(AccountType.LIABILITY))

    def total_equity(self) -> float:
        """total Equity ."""
        return sum(a.balance for a in self.by_type(AccountType.EQUITY))

    def net_income(self) -> float:
        """Revenue minus expenses."""
        revenue = sum(a.balance for a in self.by_type(AccountType.REVENUE))
        expenses = sum(a.balance for a in self.by_type(AccountType.EXPENSE))
        return revenue - expenses

    @property
    def account_count(self) -> int:
        """account Count ."""
        return len(self._accounts)

    def all_accounts(self) -> list[Account]:
        """all Accounts ."""
        return list(self._accounts.values())

    def summary(self) -> dict[str, Any]:
        """summary ."""
        return {
            "total_accounts": self.account_count,
            "assets": self.total_assets(),
            "liabilities": self.total_liabilities(),
            "equity": self.total_equity(),
            "net_income": self.net_income(),
        }
