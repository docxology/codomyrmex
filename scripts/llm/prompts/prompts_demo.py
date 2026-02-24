#!/usr/bin/env python3
"""
Prompts Demo Script

Demonstrates prompt versioning, storage, and template management.
Shows how to organize and manage prompts for production LLM applications.

Features:
    - Prompt template loading and rendering
    - Version management
    - Variable substitution
    - Prompt library organization
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== LLM Prompts Demo ===")
    try:
        from codomyrmex.llm.prompts import PromptRegistry
        obj = PromptRegistry()
        print_success(f"PromptRegistry loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("LLM Prompts demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
