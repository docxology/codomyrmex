"""Close pyplot figures that a test leaves registered.

pyplot keeps every ``plt.figure()``/``plt.subplots()`` figure until it is
closed. Figures leaked by any earlier test on the same pytest-xdist worker
therefore accumulate. Past 20, matplotlib warns ``More than 20 figures have
been opened``, and ``filterwarnings = error`` makes that fail whichever later
test opens the next figure, depending only on worker scheduling (observed in
``tests/unit/manuscript/test_figures.py``). ``tests/conftest.py`` calls this
around every test.
"""

from __future__ import annotations

import sys
from types import ModuleType


def close_loaded_figures() -> int:
    """Close all pyplot figures and return how many were open.

    pyplot is not imported here: a test process that never loaded it has no
    figures to close and should not pay for the import.
    """
    pyplot: ModuleType | None = sys.modules.get("matplotlib.pyplot")
    if pyplot is None:
        return 0
    open_figures = len(pyplot.get_fignums())
    if open_figures:
        pyplot.close("all")
    return open_figures
