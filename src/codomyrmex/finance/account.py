from enum import Enum, auto

class AccountType(Enum):
    """Primary account types in double-entry bookkeeping."""
    ASSET = auto()
    LIABILITY = auto()
    EQUITY = auto()
    REVENUE = auto()
    EXPENSE = auto()

class Account:
    """Represents a financial account."""
    
    def __init__(self, name: str, account_type: AccountType):
        self.name = name
        self.account_type = account_type
        self.balance: float = 0.0

    def __repr__(self) -> str:
        return f"Account(name='{self.name}', type={self.account_type.name})"
