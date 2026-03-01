#!/usr/bin/env python3
"""
FPF (First Principles Framework) utilities.

Usage:
    python fpf_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse


def analyze_principles(path: str = ".") -> dict:
    """Analyze first principles in codebase."""
    p = Path(path)
    
    analysis = {
        "modules": 0,
        "interfaces": 0,
        "abstractions": 0,
        "patterns": []
    }
    
    # Count Python modules
    py_files = list(p.rglob("*.py"))
    analysis["modules"] = len([f for f in py_files if "__pycache__" not in str(f)])
    
    # Look for interface patterns
    for f in py_files[:50]:
        try:
            content = f.read_text()
            if "ABC" in content or "abstractmethod" in content:
                analysis["abstractions"] += 1
            if "Protocol" in content:
                analysis["interfaces"] += 1
            if "Factory" in f.name or "factory" in content.lower():
                if "Factory" not in analysis["patterns"]:
                    analysis["patterns"].append("Factory")
            if "Singleton" in content or "_instance" in content:
                if "Singleton" not in analysis["patterns"]:
                    analysis["patterns"].append("Singleton")
        except:
            pass
    
    return analysis


def check_modularity(path: str = ".") -> dict:
    """Check module structure and dependencies."""
    p = Path(path)
    
    modules = {}
    for init in p.rglob("__init__.py"):
        if "__pycache__" not in str(init):
            module_dir = init.parent
            files = list(module_dir.glob("*.py"))
            modules[str(module_dir.relative_to(p))] = {
                "files": len(files),
                "has_tests": (module_dir / "tests").exists() or (module_dir / "test").exists(),
            }
    
    return modules


def main():
    parser = argparse.ArgumentParser(description="FPF utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze principles")
    analyze.add_argument("path", nargs="?", default=".")
    
    # Check command
    check = subparsers.add_parser("check", help="Check modularity")
    check.add_argument("path", nargs="?", default=".")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🧠 FPF Utilities\n")
        print("First Principles Framework analysis tools.\n")
        print("Commands:")
        print("  analyze - Analyze codebase principles")
        print("  check   - Check module structure")
        return 0
    
    if args.command == "analyze":
        analysis = analyze_principles(args.path)
        print(f"🧠 FPF Analysis: {args.path}\n")
        print(f"   Modules: {analysis['modules']}")
        print(f"   Interfaces: {analysis['interfaces']}")
        print(f"   Abstractions: {analysis['abstractions']}")
        if analysis["patterns"]:
            print(f"   Patterns found: {', '.join(analysis['patterns'])}")
    
    elif args.command == "check":
        modules = check_modularity(args.path)
        print(f"📦 Module Structure ({len(modules)} modules):\n")
        for name, info in list(modules.items())[:15]:
            tests = "✓ tests" if info["has_tests"] else ""
            print(f"   {name}: {info['files']} files {tests}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
