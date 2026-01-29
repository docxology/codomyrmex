#!/usr/bin/env python3
"""
Tree-sitter parsing utilities.

Usage:
    python tree_utils.py <file> [--query QUERY]
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
import re


def parse_python_ast(path: Path) -> dict:
    """Parse Python file and extract structure."""
    with open(path) as f:
        source = f.read()
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}"}
    
    structure = {
        "imports": [],
        "functions": [],
        "classes": [],
        "variables": [],
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                structure["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                structure["imports"].append(f"{module}.{alias.name}")
        elif isinstance(node, ast.FunctionDef):
            structure["functions"].append({
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "line": node.lineno,
            })
        elif isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            structure["classes"].append({
                "name": node.name,
                "methods": methods,
                "line": node.lineno,
            })
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            structure["variables"].append(node.targets[0].id)
    
    return structure


def search_pattern(path: Path, pattern: str) -> list:
    """Search for pattern in code."""
    with open(path) as f:
        lines = f.readlines()
    
    matches = []
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line):
            matches.append({"line": i, "content": line.strip()})
    
    return matches


def main():
    parser = argparse.ArgumentParser(description="Tree-sitter parsing utilities")
    parser.add_argument("file", nargs="?", help="File to parse")
    parser.add_argument("--query", "-q", help="Search pattern")
    parser.add_argument("--structure", "-s", action="store_true", help="Show structure")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if not args.file:
        print("🌳 Tree Utilities\n")
        print("Usage:")
        print("  python tree_utils.py module.py --structure")
        print("  python tree_utils.py module.py --query 'def.*async'")
        print("\nNote: Uses Python AST (tree-sitter available via codomyrmex)")
        return 0
    
    path = Path(args.file)
    if not path.exists():
        print(f"❌ File not found: {args.file}")
        return 1
    
    if args.query:
        matches = search_pattern(path, args.query)
        print(f"🔍 Pattern: {args.query}\n")
        print(f"   Found {len(matches)} matches in {path.name}:\n")
        for m in matches[:20]:
            print(f"   L{m['line']:4d}: {m['content'][:60]}")
        return 0
    
    if path.suffix == ".py":
        structure = parse_python_ast(path)
        
        if args.json:
            import json
            print(json.dumps(structure, indent=2))
            return 0
        
        print(f"🌳 Structure: {path.name}\n")
        
        if "error" in structure:
            print(f"   ❌ {structure['error']}")
            return 1
        
        if structure["imports"]:
            print(f"   📦 Imports ({len(structure['imports'])}):")
            for imp in structure["imports"][:10]:
                print(f"      - {imp}")
        
        if structure["classes"]:
            print(f"\n   🏛️  Classes ({len(structure['classes'])}):")
            for cls in structure["classes"]:
                print(f"      {cls['name']} (line {cls['line']})")
                for m in cls["methods"][:5]:
                    print(f"         - {m}()")
        
        if structure["functions"]:
            print(f"\n   🔧 Functions ({len(structure['functions'])}):")
            for func in structure["functions"][:10]:
                args_str = ", ".join(func["args"][:3])
                print(f"      {func['name']}({args_str}) @ L{func['line']}")
    else:
        print(f"📄 File: {path.name}")
        print(f"   Size: {path.stat().st_size} bytes")
        print(f"   Note: Only Python parsing supported in this utility")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
