#!/usr/bin/env python3
"""
Code quality utilities for formatting and linting.

Usage:
    python code_quality.py <path> [--fix] [--type TYPE]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess


def run_tool(cmd: list, cwd: str = ".") -> tuple:
    """Run a tool and return (success, output)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=120)
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, f"Tool not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


def check_black(path: str, fix: bool = False) -> dict:
    """Run Black formatter."""
    cmd = ["black", "--check" if not fix else "", path]
    cmd = [c for c in cmd if c]
    success, output = run_tool(cmd)
    return {"tool": "black", "success": success, "output": output}


def check_ruff(path: str, fix: bool = False) -> dict:
    """Run Ruff linter."""
    cmd = ["ruff", "check", path]
    if fix:
        cmd.append("--fix")
    success, output = run_tool(cmd)
    return {"tool": "ruff", "success": success, "output": output}


def check_isort(path: str, fix: bool = False) -> dict:
    """Run isort import sorter."""
    cmd = ["isort", "--check-only" if not fix else "", path]
    cmd = [c for c in cmd if c]
    success, output = run_tool(cmd)
    return {"tool": "isort", "success": success, "output": output}


TOOLS = {
    "black": check_black,
    "ruff": check_ruff,
    "isort": check_isort,
}


def main():
    parser = argparse.ArgumentParser(description="Code quality checks")
    parser.add_argument("path", nargs="?", default=".", help="File or directory")
    parser.add_argument("--fix", "-f", action="store_true", help="Auto-fix issues")
    parser.add_argument("--type", "-t", choices=list(TOOLS.keys()) + ["all"], default="all")
    args = parser.parse_args()
    
    if args.path == "." and not Path("pyproject.toml").exists():
        print("🔧 Code Quality Tools\n")
        print("Usage:")
        print("  python code_quality.py src/")
        print("  python code_quality.py src/ --fix")
        print("  python code_quality.py script.py --type black")
        print("\nTools: black (formatting), ruff (linting), isort (imports)")
        return 0
    
    target = Path(args.path)
    if not target.exists():
        print(f"❌ Path not found: {args.path}")
        return 1
    
    mode = "fixing" if args.fix else "checking"
    print(f"🔧 Code Quality ({mode}): {target}\n")
    
    tools_to_run = TOOLS if args.type == "all" else {args.type: TOOLS[args.type]}
    
    all_passed = True
    
    for name, check_fn in tools_to_run.items():
        result = check_fn(str(target), args.fix)
        
        if result["success"]:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name}")
            all_passed = False
            
            # Show first few lines of output
            lines = result["output"].strip().split("\n")
            for line in lines[:5]:
                print(f"      {line}")
            if len(lines) > 5:
                print(f"      ... ({len(lines) - 5} more lines)")
    
    print()
    
    if all_passed:
        print("✅ All checks passed")
    else:
        print("❌ Some checks failed")
        if not args.fix:
            print("   Run with --fix to auto-fix issues")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
