#!/usr/bin/env python3
"""
CLI utilities and helpers.

Usage:
    python cli_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import shutil


def get_terminal_size() -> tuple:
    """Get terminal dimensions."""
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines


def print_table(headers: list, rows: list, widths: list = None):
    """Print formatted table."""
    if not widths:
        widths = [max(len(str(r[i])) for r in [headers] + rows) + 2 for i in range(len(headers))]
    
    header_row = "".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_row)
    print("-" * sum(widths))
    for row in rows:
        print("".join(str(c).ljust(w) for c, w in zip(row, widths)))


def print_progress(current: int, total: int, width: int = 40):
    """Print progress bar."""
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    print(f"\r[{bar}] {pct:.0%} ({current}/{total})", end="", flush=True)


def colorize(text: str, color: str) -> str:
    """Add ANSI color to text."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def main():
    parser = argparse.ArgumentParser(description="CLI utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Demo table
    subparsers.add_parser("demo-table", help="Demo table output")
    
    # Demo progress
    subparsers.add_parser("demo-progress", help="Demo progress bar")
    
    # Demo colors
    subparsers.add_parser("demo-colors", help="Demo colors")
    
    # Terminal info
    subparsers.add_parser("info", help="Show terminal info")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🖥️  CLI Utilities\n")
        print("Commands:")
        print("  info          - Show terminal info")
        print("  demo-table    - Demo table output")
        print("  demo-progress - Demo progress bar")
        print("  demo-colors   - Demo ANSI colors")
        return 0
    
    if args.command == "info":
        cols, rows = get_terminal_size()
        print(f"🖥️  Terminal Info:\n")
        print(f"   Size: {cols}x{rows}")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   Platform: {sys.platform}")
    
    elif args.command == "demo-table":
        headers = ["Name", "Status", "Score"]
        rows = [
            ["Alpha", "Active", 95],
            ["Beta", "Pending", 82],
            ["Gamma", "Complete", 100],
        ]
        print("📊 Table Demo:\n")
        print_table(headers, rows)
    
    elif args.command == "demo-progress":
        import time
        print("📊 Progress Demo:\n")
        for i in range(101):
            print_progress(i, 100)
            time.sleep(0.02)
        print("\n\n   Done!")
    
    elif args.command == "demo-colors":
        print("🎨 Color Demo:\n")
        for color in ["red", "green", "yellow", "blue", "magenta", "cyan"]:
            print(f"   {colorize(color.capitalize(), color)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
