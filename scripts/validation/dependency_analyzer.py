#!/usr/bin/env python3
"""Analyze module dependency hierarchy and detect circular imports.

This script scans Python modules to:
- Build a dependency graph
- Detect circular imports
- Identify architecture layer violations
"""

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path


def _module_name(file_path: Path, src_dir: Path) -> str:
    """Return the package-relative module name for a Python file."""
    rel_path = file_path.relative_to(src_dir)
    parts = list(rel_path.parts[:-1])
    if file_path.name != "__init__.py":
        parts.append(file_path.stem)
    return ".".join(parts) if parts else "codomyrmex"


def _resolve_relative_import(
    module_name: str, level: int, imported_module: str | None
) -> str:
    """Resolve an AST relative import against its containing module."""
    package_parts = module_name.split(".")[:-1]
    if level > 1:
        package_parts = package_parts[: -(level - 1)]
    if imported_module:
        package_parts.extend(imported_module.split("."))
    return ".".join(part for part in package_parts if part)


def extract_imports(file_path: Path, src_dir: Path) -> set[str]:
    """Extract normalized package-relative imports from a Python file."""
    imports = set()
    module_name = _module_name(file_path, src_dir)

    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported = alias.name
                if imported == "codomyrmex":
                    continue
                if imported.startswith("codomyrmex."):
                    imports.add(imported.removeprefix("codomyrmex."))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                relative_base = _resolve_relative_import(
                    module_name, node.level, node.module
                )
                if relative_base:
                    imports.add(relative_base)
                if node.module is None and relative_base:
                    imports.update(
                        f"{relative_base}.{alias.name}" for alias in node.names
                    )
            elif node.module == "codomyrmex":
                imports.update(alias.name for alias in node.names)
            elif node.module and node.module.startswith("codomyrmex."):
                imports.add(node.module.removeprefix("codomyrmex."))

    return imports


def build_dependency_graph(src_dir: Path) -> dict[str, set[str]]:
    """Build a dependency graph from source files."""
    graph = defaultdict(set)

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            module_name = _module_name(py_file, src_dir)
        except ValueError:
            continue

        # The package root and this repository-level pytest hook are support
        # files, not runtime modules. Including them creates a misleading
        # 132-module top-level inventory (and can make package imports look
        # circular even when the production graph is not).
        if py_file == src_dir / "__init__.py" or py_file.name == "conftest.py":
            continue

        graph[module_name] = extract_imports(py_file, src_dir)

    # Reduce imports to the nearest known internal module and discard self
    # edges. The old top-level-only parser turned ``cache`` imports into
    # false ``cache -> cache`` cycles.
    known_modules = set(graph)
    for module, imports in graph.items():
        normalized: set[str] = set()
        for imported in imports:
            candidate = imported
            while candidate and candidate not in known_modules:
                candidate = candidate.rpartition(".")[0]
            if candidate and candidate != module:
                normalized.add(candidate)
        graph[module] = normalized

    return dict(graph)


def find_cycles(
    graph: dict[str, set[str]], start: str, visited: set[str], path: list
) -> list:
    """Find cycles in the dependency graph using DFS."""
    cycles = []

    if start in visited:
        if start in path:
            cycle_start = path.index(start)
            cycles.append([*path[cycle_start:], start])
        return cycles

    visited.add(start)
    path.append(start)

    for dep in graph.get(start, set()):
        if dep in graph:  # Only follow internal dependencies
            cycles.extend(find_cycles(graph, dep, visited.copy(), path.copy()))

    return cycles


def analyze_dependencies(repo_root: Path, output: Path | None = None) -> int:
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

    # Deduplicate cycles by rotation and direction rather than sorting, which
    # can collapse distinct cycles with the same members.
    unique_cycles = []
    seen_cycles: set[tuple[str, ...]] = set()
    for cycle in all_cycles:
        ring = cycle[:-1]
        rotations = [tuple(ring[i:] + ring[:i]) for i in range(len(ring))]
        normalized = (*min(rotations), min(rotations))
        if normalized not in seen_cycles:
            seen_cycles.add(normalized)
            unique_cycles.append(cycle)

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                {
                    "module_count": len(graph),
                    "top_level_modules": sorted(
                        {module.split(".")[0] for module in graph}
                    ),
                    "cycles": unique_cycles,
                    "graph": {key: sorted(value) for key, value in graph.items()},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

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
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "validation"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/validation/config.yaml")

    parser = argparse.ArgumentParser(description="Analyze module dependency hierarchy")
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="Repository root directory"
    )
    parser.add_argument(
        "--output", type=Path, help="Output file for dependency graph (JSON)"
    )

    args = parser.parse_args()

    return analyze_dependencies(args.repo_root, args.output)


if __name__ == "__main__":
    sys.exit(main())
