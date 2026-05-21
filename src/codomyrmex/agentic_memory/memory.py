"""Deprecated re-export shim for ``codomyrmex.agentic_memory.core.memory``.

The canonical implementation lives at
``codomyrmex.agentic_memory.core.memory``.  This module previously held a
byte-identical duplicate of that file (528 lines).  It is preserved only
as a thin re-export so existing imports of the form
``from codomyrmex.agentic_memory.memory import X`` keep working.

New code should import from ``codomyrmex.agentic_memory.core.memory``
directly.  This shim re-exports both the public ``__all__`` surface and
the private ``_relevance`` / ``_recency_score`` helpers, which are used
by ``tests/unit/agentic_memory/test_memory_helpers.py``.
"""

from codomyrmex.agentic_memory.core.memory import *
from codomyrmex.agentic_memory.core.memory import (
    _recency_score,
    _relevance,
)
