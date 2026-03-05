"""Graph algorithms shared across orchestrator and swarm modules."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


def kahn_topological_sort(
    nodes: Iterable[str],
    deps_of: Callable[[str], Iterable[str]],
) -> list[str]:
    """Return *nodes* in topological order using Kahn's BFS algorithm.

    Args:
        nodes: All node identifiers.
        deps_of: Callable returning the dependency identifiers for a node.
            Unrecognised dependency IDs are silently ignored so callers can
            filter externally or rely on this behaviour.
        Returns:
        Node identifiers ordered so every dependency appears before the node
        that depends on it.

    Raises:
        ValueError: When the graph contains a cycle.  The exception message
            includes the unprocessed node IDs.  Callers should convert this to
            their domain-specific exception type.

    """
    all_nodes = list(nodes)
    node_set = set(all_nodes)

    in_degree: dict[str, int] = dict.fromkeys(all_nodes, 0)
    successors: dict[str, list[str]] = {n: [] for n in all_nodes}

    for node in all_nodes:
        for dep in deps_of(node):
            if dep in node_set:
                successors[dep].append(node)
                in_degree[node] += 1

    queue: deque[str] = deque(n for n, d in in_degree.items() if d == 0)
    order: list[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for successor in successors[node]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    if len(order) != len(all_nodes):
        cyclic = sorted(node_set - set(order))
        raise ValueError(f"Cycle detected involving nodes: {cyclic}")

    return order


__all__ = ["kahn_topological_sort"]
