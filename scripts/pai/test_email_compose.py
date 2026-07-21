#!/usr/bin/env python3
"""LLM Email Compose — Functional Test Suite.

Thin wrapper — test logic has moved to::

    tests / integration / pai / test_email_compose.py

Run directly::

    uv run python -m pytest tests/integration/pai/test_email_compose.py -v

Or via this legacy entry point::

    uv run python scripts/pai/test_email_compose.py [args]
"""

import sys
from pathlib import Path

# Ensure the repository root is on the import path for the relocated test module.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# Delegate to the relocated module
from tests.integration.pai.test_email_compose import main

if __name__ == "__main__":
    sys.exit(main())
