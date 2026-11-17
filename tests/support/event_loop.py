"""Give the test session a current event loop without a deprecated implicit one.

Synchronous helpers under test still call ``asyncio.get_event_loop()``, so the
session sets one loop that ``tests/conftest.py`` owns and closes at
``pytest_sessionfinish``. Probing for an existing loop is version-dependent
when none is set on the main thread: Python 3.12–3.13 emit
``DeprecationWarning: There is no current event loop`` and then create an
untracked loop, and Python 3.14+ raise ``RuntimeError``.

pytest 9.2 applies the ``filterwarnings = error`` ini setting during
``pytest_configure``. The unguarded probe then aborted every 3.12/3.13 session
with exit 3 before collection. The probe below makes that one warning an
exception inside a local ``catch_warnings`` block, so every version reaches
the same branch and never gets a loop the harness cannot close. Global warning
filters stay unchanged.
"""

from __future__ import annotations

import asyncio
import warnings


def ensure_current_event_loop() -> asyncio.AbstractEventLoop | None:
    """Set and return a new loop when the thread has none; else return ``None``.

    An existing current loop (for example one a plugin set) is left in place
    and not returned, because its owner closes it.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            asyncio.get_event_loop()
        except (RuntimeError, DeprecationWarning):
            pass
        else:
            return None
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop
