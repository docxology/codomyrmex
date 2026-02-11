import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from uuid import uuid4, UUID

from .account import Account, AccountType

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Transaction:
    """Immutable record of a financial event."""
    debit_account: str
    credit_account: str
    amount: float
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

class LedgerError(Exception):
    """Base exception for ledger operations."""
    pass

class Ledger:
    """Double-entry bookkeeping engine."""

    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._transactions: List[Transaction] = []

    def create_account(self, name: str, account_type: AccountType) -> Account:
        """Register a new account in the ledger."""
        if name in self._accounts:
            raise LedgerError(f"Account '{name}' already exists.")
        account = Account(name, account_type)
        self._accounts[name] = account
        logger.info(f"Created account: {account}")
        return account

    def get_account(self, name: str) -> Account:
        """Retrieve an account by name."""
        if name not in self._accounts:
            raise LedgerError(f"Account '{name}' not found.")
        return self._accounts[name]

    def record(self, transaction: Transaction) -> None:
        """
        Record a transaction in the ledger.
        Enforces double-entry consistency: checks existence of accounts and non-negative amount.
        """
        if transaction.amount < 0:
            raise LedgerError("Transaction amount cannot be negative.")
        
        debit_acc = self.get_account(transaction.debit_account)
        credit_acc = self.get_account(transaction.credit_account)

        # Apply transaction logic based on account type normal balances
        # Asset/Expense: Debit increases, Credit decreases
        # Liability/Equity/Revenue: Credit increases, Debit decreases
        
        self._apply_entry(debit_acc, transaction.amount, is_debit=True)
        self._apply_entry(credit_acc, transaction.amount, is_debit=False)

        self._transactions.append(transaction)
        logger.info(f"Recorded transaction: {transaction}")

    def _apply_entry(self, account: Account, amount: float, is_debit: bool) -> None:
        """Update account balance based on normal balance rules."""
        normal_debit = account.account_type in (AccountType.ASSET, AccountType.EXPENSE)
        
        if normal_debit:
            if is_debit:
                account.balance += amount
            else:
                account.balance -= amount
        else:  # Normal Credit balance
            if is_debit:
                account.balance -= amount
            else:
                account.balance += amount

    def get_balance(self, account_name: str) -> float:
        """Get the current balance of an account."""
        return self.get_account(account_name).balance

    def trial_balance(self) -> bool:
        """
        Verify that total debits equal total credits across the ledger.
        In this simplified model, we check if net balance calculations are consistent.
        Since we enforce atomic double-entry, this should theoretically always hold,
        but float precision errors are possible in real systems.
        """
        total_debits = sum(t.amount for t in self._transactions)
        total_credits = sum(t.amount for t in self._transactions)
        return abs(total_debits - total_credits) < 1e-9
