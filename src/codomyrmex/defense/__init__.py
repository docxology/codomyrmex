"""Defense Module.

Provides Active Countermeasures and Rabbit Hole containment.

.. deprecated::
    This module is being restructured into ``security.ai_safety``.
    Import from ``codomyrmex.security.ai_safety`` instead.
    This module remains functional for backward compatibility.
"""

import warnings as _warnings

_warnings.warn(
    "codomyrmex.defense is deprecated. Use codomyrmex.security.ai_safety instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .active import ActiveDefense
from .rabbithole import RabbitHole

__all__ = ["ActiveDefense", "RabbitHole"]
