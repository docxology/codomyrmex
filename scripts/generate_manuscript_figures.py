#!/usr/bin/env python3
"""Generate publication-quality figures for the Codomyrmex manuscript.

Thin orchestrator: figure builders live in ``codomyrmex.manuscript.figures``.
"""

from __future__ import annotations

import argparse

from codomyrmex.manuscript.figures import FIGURES
from codomyrmex.manuscript.figures import main as generate_figures


def main(argv: list[str] | None = None) -> int:
    """Generate all configured figures, or describe the figure registry."""
    parser = argparse.ArgumentParser(
        description="Generate source-bound Codomyrmex manuscript figures."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List configured figure filenames without writing artifacts.",
    )
    args = parser.parse_args(argv)
    if args.list:
        for filename, _generator in FIGURES:
            print(filename)
        return 0
    generate_figures()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
