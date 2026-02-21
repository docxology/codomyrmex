# DEPRECATED(v0.2.0): Shim module. Import from codomyrmex.relations.crm.crm instead. Will be removed in v0.3.0.
"""
Backward-compatibility shim.

This module has been moved to codomyrmex.relations.crm.crm.
All imports are re-exported here for backward compatibility.
"""

from codomyrmex.relations.crm.crm import (  # noqa: F401
    Contact,
    ContactManager,
    Interaction,
)
