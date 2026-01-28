#!/usr/bin/env python3
"""
Shim for checking module health.
Wraps src/codomyrmex/documentation/scripts/bootstrap_agents_readmes.py
"""
import sys
from pathlib import Path

# Add project root to sys.path (scripts/documentation/ -> scripts/ -> repo root)
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.documentation.scripts.bootstrap_agents_readmes import main

if __name__ == "__main__":
    sys.exit(main())
