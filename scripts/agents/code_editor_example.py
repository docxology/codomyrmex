#!/usr/bin/env python3
"""
CodeEditor Agent Example

Demonstrates basic usage of CodeEditor for code generation and refactoring.
This script handles gracefully when LLM APIs are not configured.
"""
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import CodeEditor
from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_error, print_info, print_warning


def main():
    setup_logging()
    print_info("Initializing CodeEditor Agent...")

    editor = CodeEditor()

    # Test connection (always passes for CodeEditor)
    if not editor.test_connection():
        print_error("CodeEditor initialization failed.")
        return 1

    # Generate code - gracefully handle when LLM is not configured
    print_info("Generating code with CodeEditor...")
    try:
        result = editor.generate_code(
            prompt="Write a Python function to reverse a string.",
            context="Use recursion if possible."
        )
        print_success("Generated Code:")
        print(result)
    except Exception as e:
        error_msg = str(e).lower()
        if "api" in error_msg or "key" in error_msg or "401" in str(e) or "authentication" in error_msg:
            print_warning(f"LLM not configured (API key issue): {e}")
            print_info("To use: configure OPENAI_API_KEY or ANTHROPIC_API_KEY")
            return 0  # Exit gracefully - expected for demo scripts
        else:
            print_error(f"CodeEditor Error: {e}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
