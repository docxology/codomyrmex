#!/usr/bin/env python3
"""Generate publication-quality figures for the Codomyrmex manuscript.

Thin orchestrator: figure builders live in ``codomyrmex.manuscript.figures``.
"""

from __future__ import annotations

from codomyrmex.manuscript.figures import main

if __name__ == "__main__":
    main()
