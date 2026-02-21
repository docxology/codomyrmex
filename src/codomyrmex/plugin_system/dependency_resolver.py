"""Plugin dependency resolution.

Resolves plugin load order based on declared dependencies,
detects circular dependencies, and generates installation plans.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResolutionStatus(Enum):
    """Status of a dependency resolution attempt."""

    RESOLVED = "resolved"
    CIRCULAR = "circular"
    MISSING = "missing"
    CONFLICT = "conflict"


@dataclass
class DependencyNode:
    """A node in the dependency graph.

    Attributes:
        name: Plugin name.
        version: Plugin version string.
        dependencies: List of required plugin names.
        optional_dependencies: Dependencies that are nice-to-have.
        conflicts: Plugins that conflict with this one.
    """

    name: str
    version: str = "0.0.0"
    dependencies: list[str] = field(default_factory=list)
    optional_dependencies: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


@dataclass
class ResolutionResult:
    """Result of dependency resolution.

    Attributes:
        status: Overall resolution status.
        load_order: Ordered list of plugin names (dependencies first).
        missing: Plugin names that are required but not registered.
        circular: List of cycles found (each a list of plugin names).
        conflicts: List of (plugin_a, plugin_b) conflicts.
    """

    status: ResolutionStatus
    load_order: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    circular: list[list[str]] = field(default_factory=list)
    conflicts: list[tuple[str, str]] = field(default_factory=list)


class DependencyResolver:
    """Resolves plugin dependencies using topological sort.

    Supports cycle detection, missing dependency reporting,
    and conflict identification.

    Example::

        resolver = DependencyResolver()
        resolver.add(DependencyNode("auth", dependencies=["db"]))
        resolver.add(DependencyNode("db"))
        result = resolver.resolve()
        # result.load_order == ["db", "auth"]
    """

    def __init__(self) -> None:
        self._nodes: dict[str, DependencyNode] = {}

    def add(self, node: DependencyNode) -> None:
        """Register a plugin with its dependencies."""
        self._nodes[node.name] = node

    def add_many(self, nodes: list[DependencyNode]) -> None:
        """Register multiple plugins."""
        for node in nodes:
            self._nodes[node.name] = node

    def get(self, name: str) -> DependencyNode | None:
        """Look up a registered plugin."""
        return self._nodes.get(name)

    @property
    def node_count(self) -> int:
        """Number of registered nodes."""
        return len(self._nodes)

    def resolve(self) -> ResolutionResult:
        """Resolve dependencies and produce a load order.

        Uses Kahn's algorithm (BFS topological sort) for stable
        ordering with cycle detection.

        Returns:
            ResolutionResult with load order or error info.
        """
        # Check for missing dependencies
        all_names = set(self._nodes.keys())
        missing: list[str] = []
        for node in self._nodes.values():
            for dep in node.dependencies:
                if dep not in all_names:
                    missing.append(dep)

        if missing:
            return ResolutionResult(
                status=ResolutionStatus.MISSING,
                missing=sorted(set(missing)),
            )

        # Check for conflicts
        conflicts: list[tuple[str, str]] = []
        for node in self._nodes.values():
            for conflict_name in node.conflicts:
                if conflict_name in all_names:
                    conflicts.append((node.name, conflict_name))

        if conflicts:
            return ResolutionResult(
                status=ResolutionStatus.CONFLICT,
                conflicts=conflicts,
            )

        # Build adjacency and in-degree maps
        in_degree: dict[str, int] = {name: 0 for name in self._nodes}
        adjacency: dict[str, list[str]] = defaultdict(list)

        for node in self._nodes.values():
            for dep in node.dependencies:
                adjacency[dep].append(node.name)
                in_degree[node.name] += 1

        # Kahn's algorithm
        queue: deque[str] = deque(
            name for name, degree in in_degree.items() if degree == 0
        )
        order: list[str] = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for dependent in adjacency[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(self._nodes):
            # Cycle detected — find the cycle members
            remaining = [n for n in self._nodes if n not in set(order)]
            cycles = self._find_cycles(remaining)
            return ResolutionResult(
                status=ResolutionStatus.CIRCULAR,
                load_order=order,
                circular=cycles,
            )

        return ResolutionResult(
            status=ResolutionStatus.RESOLVED,
            load_order=order,
        )

    def _find_cycles(self, nodes: list[str]) -> list[list[str]]:
        """Find cycles among a set of nodes using DFS."""
        visited: set[str] = set()
        cycles: list[list[str]] = []

        for start in nodes:
            if start in visited:
                continue
            path: list[str] = []
            self._dfs_cycle(start, path, visited, set(), cycles)

        return cycles

    def _dfs_cycle(
        self,
        node: str,
        path: list[str],
        visited: set[str],
        in_stack: set[str],
        cycles: list[list[str]],
    ) -> None:
        """DFS helper for cycle detection."""
        visited.add(node)
        in_stack.add(node)
        path.append(node)

        node_data = self._nodes.get(node)
        if node_data:
            for dep in node_data.dependencies:
                if dep in in_stack:
                    idx = path.index(dep)
                    cycles.append(path[idx:] + [dep])
                elif dep not in visited and dep in self._nodes:
                    self._dfs_cycle(dep, path, visited, in_stack, cycles)

        path.pop()
        in_stack.discard(node)

    def clear(self) -> None:
        """Remove all registered nodes."""
        self._nodes.clear()
