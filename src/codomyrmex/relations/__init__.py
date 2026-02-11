"""Relations Module for Codomyrmex.

Provides CRM, social media management, and network analysis.
"""

# Lazy imports
try:
    from .crm import Contact
except ImportError:
    Contact = None

__all__ = ["Contact"]
