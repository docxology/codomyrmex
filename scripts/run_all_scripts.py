#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# [tool.uv]
# dev-dependencies = []
# ///
"""
Master Script Orchestrator (thin wrapper).

Delegates to ``codomyrmex.orchestrator.core.main``. A missing-mode invocation
(no ``--dry-run``, ``--subdirs``, or ``--filter``) defaults to ``--dry-run`` so
the script never runs the whole ``scripts/`` tree implicitly; see the
mutation-boundary rules in ``scripts/README.md``.

Usage:
    uv run --locked python scripts/run_all_scripts.py --dry-run
    uv run --locked python scripts/run_all_scripts.py --subdirs documentation
    uv run --locked python scripts/run_all_scripts.py --filter audit --timeout 60
"""

import sys
from pathlib import Path

try:
    from codomyrmex.orchestrator.core import main
except ImportError as e:
    print(
        "Error: Could not import codomyrmex.orchestrator. "
        "Run with 'uv run --locked python scripts/run_all_scripts.py' so the "
        "project package is importable.",
        file=sys.stderr,
    )
    print(f"Traceback: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    argv = sys.argv[1:]

    # Missing-mode invocations stay read-only: no explicit scope means dry-run.
    if not any(
        arg == "--dry-run" or arg.startswith(("--subdirs", "--filter")) for arg in argv
    ):
        argv.append("--dry-run")

    # Pass the directory of this script so the orchestrator knows where to search.
    if "--scripts-dir" not in argv:
        argv.append(f"--scripts-dir={Path(__file__).resolve().parent}")

    if "--timeout" not in argv:
        argv.extend(["--timeout", "120"])

    sys.exit(main(argv))
