"""Module dependency mapper — AST-based import graph analysis.

Builds a directed dependency graph from Python import statements
across all Codomyrmex modules. Detects circular dependencies.

Example::

    mapper = DependencyMapper()
    graph = mapper.build_graph()
    print(f"Edges: {graph['total_edges']}")
    for cycle in graph["cycles"]:
        print(f"  Circular: {' → '.join(cycle)}")
"""

from __future__ import annotations

import ast
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SRC_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ImportEdge:
    """A single import relationship.

    Attributes:
        source: Importing module name.
        target: Imported module name.
        import_type: ``"absolute"`` or ``"relative"``.
    """

    source: str
    target: str
    import_type: str = "absolute"


class DependencyMapper:
    """AST-based import graph builder for Codomyrmex modules.

    Args:
        src_root: Path to ``src/codomyrmex/``.

    Example::

        mapper = DependencyMapper()
        graph = mapper.build_graph()
        deps = mapper.get_dependencies("agents")  # What does 'agents' depend on?
        dependents = mapper.get_dependents("utils")  # What depends on 'utils'?
    """

    def __init__(self, src_root: Path | None = None) -> None:
        self._root = src_root or _SRC_ROOT

    def _extract_imports(self, filepath: Path) -> list[str]:
        """Extract codomyrmex imports from a Python file."""
        try:
            tree = ast.parse(filepath.read_text(errors="replace"))
        except Exception:
            return []

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("codomyrmex."):
                        parts = alias.name.split(".")
                        if len(parts) >= 2:
                            imports.append(parts[1])
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("codomyrmex."):
                    parts = node.module.split(".")
                    if len(parts) >= 2:
                        imports.append(parts[1])

        return list(set(imports))

    def build_graph(self) -> dict[str, Any]:
        """Build the full dependency graph.

        Returns:
            dict with ``total_modules``, ``total_edges``,
            ``edges``, ``in_degree``, ``out_degree``, ``cycles``.
        """
        start = time.monotonic()
        edges: list[dict] = []
        adjacency: dict[str, set[str]] = defaultdict(set)
        modules: set[str] = set()

        for mod_dir in sorted(self._root.iterdir()):
            if (
                not mod_dir.is_dir()
                or mod_dir.name.startswith(("_", "."))
                or mod_dir.name == "tests"
            ):
                continue

            modules.add(mod_dir.name)
            for py_file in mod_dir.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue
                imports = self._extract_imports(py_file)
                for imp in imports:
                    if (imp != mod_dir.name and imp in modules) or self._is_module(imp):
                        adjacency[mod_dir.name].add(imp)
                        edges.append(
                            {
                                "source": mod_dir.name,
                                "target": imp,
                            }
                        )

        # Calculate degrees
        in_degree: dict[str, int] = defaultdict(int)
        out_degree: dict[str, int] = defaultdict(int)
        for src, targets in adjacency.items():
            out_degree[src] = len(targets)
            for t in targets:
                in_degree[t] += 1

        # Detect cycles (simple DFS)
        cycles = self._find_cycles(adjacency)

        elapsed = (time.monotonic() - start) * 1000
        return {
            "total_modules": len(modules),
            "total_edges": len(edges),
            "cycles": cycles,
            "cycle_count": len(cycles),
            "top_imported": sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
            "top_importers": sorted(
                out_degree.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "scan_duration_ms": round(elapsed, 1),
        }

    def _is_module(self, name: str) -> bool:
        """Check if a name corresponds to a codomyrmex module."""
        return (self._root / name).is_dir()

    def _find_cycles(self, adj: dict[str, set[str]]) -> list[list[str]]:
        """Find circular dependencies using DFS."""
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []
        path: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adj.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    idx = path.index(neighbor) if neighbor in path else -1
                    if idx >= 0:
                        cycle = [*path[idx:], neighbor]
                        if len(cycle) <= 5 and cycle not in cycles:
                            cycles.append(cycle)

            path.pop()
            rec_stack.discard(node)

        for node in adj:
            if node not in visited:
                dfs(node)

        return cycles[:20]  # Cap at 20 cycles

    def get_dependencies(self, module: str) -> list[str]:
        """Get direct dependencies of a module.

        Args:
            module: Module name.

        Returns:
            list of module names this module imports from.
        """
        mod_dir = self._root / module
        if not mod_dir.exists():
            return []

        deps: set[str] = set()
        for py_file in mod_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            deps.update(self._extract_imports(py_file))

        deps.discard(module)  # Remove self-references
        return sorted(deps)

    def get_dependents(self, module: str) -> list[str]:
        """Get modules that depend on the given module.

        Args:
            module: Module name.

        Returns:
            list of module names that import from this module.
        """
        dependents: set[str] = set()

        for mod_dir in self._root.iterdir():
            if (
                not mod_dir.is_dir()
                or mod_dir.name.startswith(("_", "."))
                or mod_dir.name == "tests"
            ):
                continue
            if mod_dir.name == module:
                continue

            for py_file in mod_dir.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue
                imports = self._extract_imports(py_file)
                if module in imports:
                    dependents.add(mod_dir.name)
                    break

        return sorted(dependents)


__all__ = [
    "DependencyMapper",
    "ImportEdge",
]
