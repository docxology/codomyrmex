"""Finance Module for Codomyrmex.

Provides double-entry bookkeeping, tax compliance, payroll processing,
and financial forecasting.

Submodules:
    ledger -- Double-entry bookkeeping engine
    forecasting -- Time-series forecasting (moving average, exponential smoothing, linear trend)
    taxes -- Progressive tax calculation with bracket support
    payroll -- Payroll processing with tax withholding and pay-stub generation
"""

from .forecasting import Forecaster, ForecastError
from .ledger import (
    Account,
    AccountType,
    Ledger,
    LedgerError,
    Transaction,
    TransactionEntry,
)
from .payroll import PayrollProcessor, PayStub, PayrollError
from .taxes import TaxCalculator, TaxResult, TaxError

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
    "ForecastError",
    # Taxes
    "TaxCalculator",
    "TaxResult",
    "TaxError",
    # Payroll
    "PayrollProcessor",
    "PayStub",
    "PayrollError",
]
