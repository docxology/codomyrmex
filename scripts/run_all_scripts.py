#!/usr/bin/env python3
"""
Master Script Orchestrator

Run and log all scripts in the scripts directory with comprehensive reporting.
Discovers Python scripts in subdirectories, executes them, and generates
execution reports with logs.

This script is now a thin wrapper around the `codomyrmex.orchestrator` module.

Usage:
    python run_all_scripts.py [--dry-run] [--timeout SECONDS] [--filter PATTERN]
    python run_all_scripts.py --subdirs documentation testing
    python run_all_scripts.py --verbose --output-dir /path/to/logs
"""

import sys
from pathlib import Path

# Add project src to sys.path to ensure we can import codomyrmex
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from codomyrmex.orchestrator.core import main
except ImportError as e:
    print(f"Error: Could not import codomyrmex.orchestrator. Ensure 'src' is in PYTHONPATH.", file=sys.stderr)
    print(f"Traceback: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    # We pass the directory of this script so the orchestrator knows where to start searching
    # (The orchestrator will fall back to heuristic discovery, but explicit is better)
    sys.argv.append(f"--scripts-dir={Path(__file__).parent}")
    if "--timeout" not in sys.argv:
        sys.argv.extend(["--timeout", "120"])
    sys.exit(main())