#!/usr/bin/env python3
"""
Terminal utilities for shell operations.

Usage:
    python terminal_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import os
import subprocess
import shutil


def get_terminal_size() -> tuple:
    """Get terminal dimensions."""
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines


def get_shell_info() -> dict:
    """Get current shell information."""
    return {
        "shell": os.environ.get("SHELL", "unknown"),
        "term": os.environ.get("TERM", "unknown"),
        "user": os.environ.get("USER", "unknown"),
        "home": os.environ.get("HOME", "unknown"),
        "path_entries": len(os.environ.get("PATH", "").split(":")),
    }


def list_processes(filter_text: str = None) -> list:
    """List running processes."""
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        lines = result.stdout.split("\n")[1:]  # Skip header
        
        processes = []
        for line in lines:
            if not line.strip():
                continue
            if filter_text and filter_text.lower() not in line.lower():
                continue
            
            parts = line.split(None, 10)
            if len(parts) >= 11:
                processes.append({
                    "user": parts[0],
                    "pid": parts[1],
                    "cpu": parts[2],
                    "mem": parts[3],
                    "command": parts[10][:60],
                })
        
        return processes
    except:
        return []


def check_command(command: str) -> bool:
    """Check if a command is available."""
    return shutil.which(command) is not None


def main():
    parser = argparse.ArgumentParser(description="Terminal utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Info command
    subparsers.add_parser("info", help="Show terminal info")
    
    # Check command
    check = subparsers.add_parser("check", help="Check if commands are available")
    check.add_argument("commands", nargs="+", help="Commands to check")
    
    # Processes command
    ps = subparsers.add_parser("ps", help="List processes")
    ps.add_argument("--filter", "-f", default=None, help="Filter processes")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🖥️  Terminal Utilities\n")
        print("Commands:")
        print("  info   - Show terminal information")
        print("  check  - Check command availability")
        print("  ps     - List processes")
        print("\nExamples:")
        print("  python terminal_utils.py info")
        print("  python terminal_utils.py check python node docker")
        print("  python terminal_utils.py ps --filter python")
        return 0
    
    if args.command == "info":
        cols, rows = get_terminal_size()
        info = get_shell_info()
        
        print("🖥️  Terminal Info\n")
        print(f"   Shell: {info['shell']}")
        print(f"   Term: {info['term']}")
        print(f"   User: {info['user']}")
        print(f"   Size: {cols}x{rows}")
        print(f"   PATH entries: {info['path_entries']}")
    
    elif args.command == "check":
        print("🔍 Command Check\n")
        for cmd in args.commands:
            available = check_command(cmd)
            icon = "✅" if available else "❌"
            location = shutil.which(cmd) if available else "not found"
            print(f"   {icon} {cmd}: {location}")
    
    elif args.command == "ps":
        processes = list_processes(args.filter)
        
        if args.filter:
            print(f"🔍 Processes matching '{args.filter}':\n")
        else:
            print("📋 Running processes:\n")
        
        print(f"   {'PID':<8} {'CPU%':<6} {'MEM%':<6} {'COMMAND'}")
        print("   " + "-" * 60)
        
        for p in processes[:20]:
            print(f"   {p['pid']:<8} {p['cpu']:<6} {p['mem']:<6} {p['command']}")
        
        if len(processes) > 20:
            print(f"\n   ... and {len(processes) - 20} more")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
