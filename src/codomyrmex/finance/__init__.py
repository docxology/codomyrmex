"""Finance Module for Codomyrmex.

Provides double-entry bookkeeping, tax compliance, payroll, and forecasting.
"""

# Lazy imports for submodules
try:
    from .ledger import Ledger
except ImportError:
    Ledger = None

__all__ = ["Ledger"]
