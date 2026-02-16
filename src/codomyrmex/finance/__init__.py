"""Finance Module for Codomyrmex.

Provides double-entry bookkeeping, tax compliance, payroll processing,
and financial forecasting.

Submodules:
    ledger -- Double-entry bookkeeping engine
    forecasting -- Time-series forecasting (moving average, exponential smoothing, linear trend)
    taxes -- Progressive tax calculation with bracket support
    payroll -- Payroll processing with tax withholding and pay-stub generation
"""

from .ledger import (
    AccountType,
    Account,
    TransactionEntry,
    Transaction,
    Ledger,
    LedgerError,
)
from .forecasting import Forecaster
from .taxes import TaxCalculator, TaxResult
from .payroll import PayrollProcessor, PayStub

__all__ = [
    # Ledger
    "AccountType",
    "Account",
    "TransactionEntry",
    "Transaction",
    "Ledger",
    "LedgerError",
    # Forecasting
    "Forecaster",
    # Taxes
    "TaxCalculator",
    "TaxResult",
    # Payroll
    "PayrollProcessor",
    "PayStub",
]
