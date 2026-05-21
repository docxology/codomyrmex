"""Deprecated re-export shim for ``codomyrmex.agentic_memory.core.models``.

The canonical implementation lives at
``codomyrmex.agentic_memory.core.models``.  This module previously held a
byte-identical 129-line duplicate of that file.  It is preserved only as a
thin re-export so existing imports of the form
``from codomyrmex.agentic_memory.models import X`` keep working AND resolve
to the SAME class objects as ``from codomyrmex.agentic_memory.core.models
import X`` — without that identity, ``isinstance()`` checks across the two
paths would fail (regression caught by R3-F).

New code should import from ``codomyrmex.agentic_memory.core.models``
directly.
"""

from codomyrmex.agentic_memory.core.models import *
