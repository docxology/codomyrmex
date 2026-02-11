"""Governance Module for Codomyrmex.

Provides contracts, policy enforcement, and dispute resolution.
"""

# Lazy imports
try:
    from .contracts import Contract
except ImportError:
    Contract = None

__all__ = ["Contract"]
