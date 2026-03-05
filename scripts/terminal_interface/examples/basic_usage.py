#!/usr/bin/env python3
"""
Terminal Interface - Real Usage Examples

Demonstrates actual terminal interface capabilities:
- TerminalFormatter for styled output
- CommandRunner for diagnostic checks
- InteractiveShell initialization
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.terminal_interface import (
    CommandRunner,
    InteractiveShell,
    TerminalFormatter,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "terminal_interface"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/terminal_interface/config.yaml")

    setup_logging()
    print_info("Running Terminal Interface Examples...")

    # 1. Terminal Formatter
    print_info("Testing TerminalFormatter...")
    try:
        formatter = TerminalFormatter(use_colors=True)
        print(formatter.header("STYLED HEADER"))
        print(formatter.success("This is a success message in green."))

        # Test progress bar
        print(
            "\n"
            + formatter.progress_bar(75, 100, prefix="Processing", suffix="Complete")
        )

        # Test table
        headers = ["Module", "Status"]
        rows = [["Core", "Active"], ["Agents", "Idle"]]
        print("\n" + formatter.table(headers, rows))

        print_success("  TerminalFormatter verified.")
    except Exception as e:
        print_error(f"  TerminalFormatter failed: {e}")

    # 2. Command Runner
    print_info("Testing CommandRunner...")
    try:
        runner = CommandRunner()
        info = runner.get_system_info()
        if info:
            print_success(
                f"  System info retrieved. OS: {info.get('platform', 'Unknown')}"
            )
    except Exception as e:
        print_error(f"  CommandRunner failed: {e}")

    # 3. Interactive Shell
    print_info("Verifying InteractiveShell initialization...")
    try:
        # Don't call .run() or .cmdloop() as it's interactive
        shell = InteractiveShell()
        if shell.prompt:
            print_success(
                f"  InteractiveShell available with prompt: {shell.prompt.strip()}"
            )
    except Exception as e:
        print_info(f"  InteractiveShell note: {e}")

    print_success("Terminal interface examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
