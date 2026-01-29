#!/usr/bin/env python3
"""
Run static analysis on Python code.

Usage:
    python analyze_code.py <path> [--type TYPE]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import ast
import subprocess


def analyze_python_file(file_path: Path) -> dict:
    """Analyze a Python file."""
    with open(file_path, "r") as f:
        source = f.read()
    
    stats = {
        "lines": len(source.split("\n")),
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "docstrings": 0,
        "todos": source.lower().count("todo"),
        "complexity_warning": False,
    }
    
    try:
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                stats["functions"] += 1
                if ast.get_docstring(node):
                    stats["docstrings"] += 1
            elif isinstance(node, ast.ClassDef):
                stats["classes"] += 1
                if ast.get_docstring(node):
                    stats["docstrings"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                stats["imports"] += 1
        
        # Simple complexity check
        if stats["functions"] > 20 or stats["lines"] > 500:
            stats["complexity_warning"] = True
            
    except SyntaxError as e:
        stats["syntax_error"] = str(e)
    
    return stats


def run_external_linter(path: str, linter: str) -> list:
    """Run an external linter."""
    cmd_map = {
        "ruff": ["ruff", "check", path],
        "flake8": ["flake8", path],
        "pylint": ["pylint", "--output-format=text", path],
        "mypy": ["mypy", path],
    }
    
    if linter not in cmd_map:
        return [f"Unknown linter: {linter}"]
    
    try:
        result = subprocess.run(cmd_map[linter], capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return [l for l in output.split("\n") if l.strip()][:20]
    except FileNotFoundError:
        return [f"{linter} not installed"]
    except Exception as e:
        return [str(e)]


def main():
    parser = argparse.ArgumentParser(description="Static code analysis")
    parser.add_argument("path", nargs="?", help="File or directory to analyze")
    parser.add_argument("--type", "-t", choices=["basic", "ruff", "flake8", "pylint", "mypy"], default="basic")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    if not args.path:
        print("🔍 Code Analyzer\n")
        print("Usage:")
        print("  python analyze_code.py src/")
        print("  python analyze_code.py script.py --type ruff")
        print("\nAnalysis types:")
        print("  basic   - Built-in AST analysis")
        print("  ruff    - Fast Python linter")
        print("  flake8  - Style guide enforcement")
        print("  pylint  - Comprehensive linting")
        print("  mypy    - Type checking")
        return 0
    
    target = Path(args.path)
    if not target.exists():
        print(f"❌ Path not found: {args.path}")
        return 1
    
    print(f"🔍 Analyzing: {target}\n")
    
    if args.type != "basic":
        results = run_external_linter(str(target), args.type)
        if results:
            print(f"📋 {args.type.upper()} results:\n")
            for r in results:
                print(f"   {r}")
            return 1 if len(results) > 1 else 0
        else:
            print(f"✅ No issues found by {args.type}")
            return 0
    
    # Basic analysis
    files = [target] if target.is_file() else list(target.rglob("*.py"))
    files = [f for f in files if "__pycache__" not in str(f)]
    
    total = {"files": 0, "lines": 0, "functions": 0, "classes": 0, "todos": 0}
    issues = []
    
    for f in files[:50]:
        stats = analyze_python_file(f)
        total["files"] += 1
        total["lines"] += stats["lines"]
        total["functions"] += stats["functions"]
        total["classes"] += stats["classes"]
        total["todos"] += stats["todos"]
        
        if "syntax_error" in stats:
            issues.append(f"{f.name}: Syntax error - {stats['syntax_error']}")
        if stats["complexity_warning"]:
            issues.append(f"{f.name}: Complexity warning (>20 functions or >500 lines)")
        
        if args.verbose:
            print(f"   📄 {f.name}: {stats['lines']} lines, {stats['functions']} funcs, {stats['classes']} classes")
    
    print(f"📊 Summary ({total['files']} files):")
    print(f"   Lines: {total['lines']:,}")
    print(f"   Functions: {total['functions']}")
    print(f"   Classes: {total['classes']}")
    if total["todos"]:
        print(f"   TODOs: {total['todos']}")
    
    if issues:
        print(f"\n⚠️  Issues ({len(issues)}):")
        for issue in issues[:10]:
            print(f"   • {issue}")
    else:
        print("\n✅ No issues detected")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
