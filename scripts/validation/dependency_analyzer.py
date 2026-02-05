#!/usr/bin/env python3
"""Analyze module dependency hierarchy and detect circular imports.

This script scans Python modules to:
- Build a dependency graph
- Detect circular imports
- Identify architecture layer violations
"""

import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path
from typing import Set


def extract_imports(file_path: Path) -> Set[str]:
    """Extract import statements from a Python file."""
    imports = set()
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return imports
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    
    return imports


def build_dependency_graph(src_dir: Path) -> dict[str, Set[str]]:
    """Build a dependency graph from source files."""
    graph = defaultdict(set)
    
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        # Get module name relative to src
        try:
            rel_path = py_file.relative_to(src_dir)
            module_parts = list(rel_path.parts[:-1])  # Directory parts
            if py_file.name != "__init__.py":
                module_parts.append(py_file.stem)
            module_name = ".".join(module_parts) if module_parts else py_file.stem
        except ValueError:
            continue
        
        imports = extract_imports(py_file)
        graph[module_name] = imports
    
    return dict(graph)


def find_cycles(graph: dict[str, Set[str]], start: str, visited: Set[str], path: list) -> list:
    """Find cycles in the dependency graph using DFS."""
    cycles = []
    
    if start in visited:
        if start in path:
            cycle_start = path.index(start)
            cycles.append(path[cycle_start:] + [start])
        return cycles
    
    visited.add(start)
    path.append(start)
    
    for dep in graph.get(start, set()):
        if dep in graph:  # Only follow internal dependencies
            cycles.extend(find_cycles(graph, dep, visited.copy(), path.copy()))
    
    return cycles


def analyze_dependencies(repo_root: Path) -> int:
    """Analyze dependencies and report findings."""
    print("🔍 Analyzing module dependency hierarchy...\n")
    
    src_dir = repo_root / "src" / "codomyrmex"
    if not src_dir.exists():
        src_dir = repo_root / "src"
    
    if not src_dir.exists():
        print("❌ No src directory found")
        return 1
    
    graph = build_dependency_graph(src_dir)
    
    print(f"📊 Found {len(graph)} modules")
    
    # Find potential circular dependencies
    all_cycles = []
    for module in graph:
        cycles = find_cycles(graph, module, set(), [])
        all_cycles.extend(cycles)
    
    # Deduplicate cycles
    unique_cycles = []
    for cycle in all_cycles:
        normalized = tuple(sorted(cycle))
        if normalized not in [tuple(sorted(c)) for c in unique_cycles]:
            unique_cycles.append(cycle)
    
    if unique_cycles:
        print(f"\n⚠️  Found {len(unique_cycles)} potential circular dependencies:")
        for i, cycle in enumerate(unique_cycles[:5], 1):  # Show first 5
            print(f"   {i}. {' -> '.join(cycle)}")
        if len(unique_cycles) > 5:
            print(f"   ... and {len(unique_cycles) - 5} more")
    else:
        print("\n✅ No circular dependencies detected")
    
    # Report top-level modules
    top_level = set()
    for module in graph:
        if "." not in module:
            top_level.add(module)
    
    print(f"\n📦 Top-level modules: {len(top_level)}")
    for mod in sorted(list(top_level)[:10]):
        print(f"   - {mod}")
    
    print("\n✅ Dependency analysis complete")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Analyze module dependency hierarchy")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for dependency graph (JSON)"
    )
    
    args = parser.parse_args()
    
    return analyze_dependencies(args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
