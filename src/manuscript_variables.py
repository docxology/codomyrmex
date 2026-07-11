"""Backward-compatibility shim for ``codomyrmex.manuscript.variables``.

Prefer: ``from codomyrmex.manuscript.variables import compute_variables``
"""

from codomyrmex.manuscript.variables import *
from codomyrmex.manuscript.variables import compute_variables, inject_via_infrastructure

__all__ = ["compute_variables", "inject_via_infrastructure"]
