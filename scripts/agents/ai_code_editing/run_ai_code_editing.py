#!/usr/bin/env python3
"""AI Code Editing — Thin Script Orchestrator.

Exercises the CodeEditor from the ai_code_editing submodule.

Usage:
    python scripts/agents/ai_code_editing/run_ai_code_editing.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("AI Code Editing — probing CodeEditor...")

    try:
        from codomyrmex.agents.ai_code_editing import CodeEditor
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success(f"CodeEditor imported: {CodeEditor.__name__}")
    print_info(f"  Methods: {[m for m in dir(CodeEditor) if not m.startswith('_')][:10]}")
    print_success("AI Code Editing probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
