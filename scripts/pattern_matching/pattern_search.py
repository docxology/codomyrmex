#!/usr/bin/env python3
"""
Search for patterns in code using regex and AST matching.

Usage:
    python pattern_search.py <pattern> [path] [--type TYPE]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import re
import ast


def search_regex(pattern: str, path: Path, file_extensions: list = None) -> list:
    """Search for regex pattern in files."""
    matches = []
    
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*"))
    
    compiled = re.compile(pattern, re.IGNORECASE)
    
    for f in files:
        if not f.is_file():
            continue
        if file_extensions and f.suffix not in file_extensions:
            continue
        if "__pycache__" in str(f) or ".git" in str(f):
            continue
        
        try:
            with open(f, "r", errors="ignore") as file:
                for i, line in enumerate(file, 1):
                    if compiled.search(line):
                        matches.append({
                            "file": str(f),
                            "line": i,
                            "content": line.strip()[:100],
                        })
        except:
            pass
    
    return matches


def search_ast_pattern(pattern_type: str, path: Path) -> list:
    """Search for AST patterns in Python files."""
    matches = []
    
    files = [path] if path.is_file() else list(path.rglob("*.py"))
    
    pattern_searches = {
        "function": ast.FunctionDef,
        "class": ast.ClassDef,
        "import": (ast.Import, ast.ImportFrom),
        "try": ast.Try,
        "with": ast.With,
        "async": (ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith),
    }
    
    target_type = pattern_searches.get(pattern_type)
    if not target_type:
        return [{"error": f"Unknown AST pattern: {pattern_type}"}]
    
    for f in files:
        if "__pycache__" in str(f):
            continue
        
        try:
            with open(f) as file:
                tree = ast.parse(file.read())
            
            for node in ast.walk(tree):
                if isinstance(node, target_type):
                    name = getattr(node, "name", None) or str(type(node).__name__)
                    matches.append({
                        "file": str(f),
                        "line": node.lineno,
                        "type": type(node).__name__,
                        "name": name,
                    })
        except:
            pass
    
    return matches


def main():
    parser = argparse.ArgumentParser(description="Search for patterns in code")
    parser.add_argument("pattern", nargs="?", help="Search pattern (regex or AST type)")
    parser.add_argument("path", nargs="?", default=".", help="Path to search")
    parser.add_argument("--type", "-t", choices=["regex", "ast"], default="regex")
    parser.add_argument("--ext", "-e", action="append", help="File extensions (e.g., .py)")
    parser.add_argument("--count", "-c", action="store_true", help="Show count only")
    args = parser.parse_args()
    
    if not args.pattern:
        print("🔎 Pattern Search\n")
        print("Usage:")
        print("  python pattern_search.py 'TODO' src/")
        print("  python pattern_search.py 'def \\w+\\(' --ext .py")
        print("  python pattern_search.py function src/ --type ast")
        print("\nAST patterns: function, class, import, try, with, async")
        return 0
    
    target = Path(args.path)
    if not target.exists():
        print(f"❌ Path not found: {args.path}")
        return 1
    
    print(f"🔎 Searching: {args.pattern}\n")
    
    if args.type == "ast":
        matches = search_ast_pattern(args.pattern, target)
    else:
        extensions = args.ext or [".py", ".js", ".ts", ".md", ".yaml", ".json"]
        matches = search_regex(args.pattern, target, extensions)
    
    if args.count:
        print(f"   Found: {len(matches)} matches")
        return 0
    
    if not matches:
        print("   No matches found")
        return 0
    
    print(f"📋 Found {len(matches)} match(es):\n")
    
    for m in matches[:30]:
        if "error" in m:
            print(f"   ❌ {m['error']}")
            continue
        
        file_path = Path(m["file"]).name
        line = m["line"]
        
        if "name" in m:
            print(f"   {file_path}:{line} - {m['type']}: {m['name']}")
        else:
            print(f"   {file_path}:{line}")
            print(f"      {m['content']}")
    
    if len(matches) > 30:
        print(f"\n   ... and {len(matches) - 30} more")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
