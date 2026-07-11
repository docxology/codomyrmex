"""Filesystem import-graph helpers for circular dependency detection."""

from __future__ import annotations

import ast
import os
from collections import deque


def _module_path_to_dir(dotted_module: str, repo_root: str) -> str | None:
    """Convert a dotted module path to a filesystem directory path.

    Searches common source tree roots (``src/``, ``src/<package>/``, repo root).
    Returns ``None`` if the directory cannot be located.
    """
    parts = dotted_module.split(".")
    candidates = [
        os.path.join(repo_root, *parts),
        os.path.join(repo_root, "src", *parts),
    ]
    # Also handle src/<top_package>/<rest>
    if parts:
        candidates.append(os.path.join(repo_root, "src", parts[0], *parts[1:]))

    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    return None


def _build_import_graph(module_dir: str) -> dict[str, list[str]]:
    """Walk *module_dir* recursively and build a module-level import graph.

    Returns a dict mapping each Python file's dotted-like key (relative to
    *module_dir*) to the list of dotted-like keys it imports.

    Only relative imports and intra-tree absolute imports are tracked.
    """
    graph: dict[str, list[str]] = {}
    base_name = os.path.basename(module_dir)

    for dirpath, _dirs, filenames in os.walk(module_dir):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, module_dir)
            # Convert path to dotted key
            node = base_name + "." + rel.replace(os.sep, ".").removesuffix(".py")
            if node.endswith(".__init__"):
                node = node.removesuffix(".__init__")
            imports: list[str] = []
            try:
                source = _read_source(fpath)
                tree = ast.parse(source, filename=fpath)
            except (OSError, SyntaxError):
                graph[node] = imports
                continue

            for ast_node in ast.walk(tree):
                if isinstance(ast_node, ast.Import):
                    for alias in ast_node.names:
                        if alias.name.startswith(base_name):
                            imports.append(alias.name)
                elif isinstance(ast_node, ast.ImportFrom):
                    if ast_node.module and ast_node.module.startswith(base_name):
                        imports.append(ast_node.module)
                    elif ast_node.level and ast_node.level > 0:
                        # Relative import — resolve approximately
                        pkg_parts = node.split(".")
                        up = ast_node.level
                        prefix = ".".join(pkg_parts[: max(1, len(pkg_parts) - up)])
                        resolved = (
                            f"{prefix}.{ast_node.module}" if ast_node.module else prefix
                        )
                        imports.append(resolved)

            graph[node] = imports

    return graph


def _read_source(path: str) -> str:
    """Read a Python source file, trying UTF-8 then latin-1."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        with open(path, encoding="latin-1") as fh:
            return fh.read()


def _find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    """Return a non-empty list of node names forming a cycle, or ``None`` if acyclic.

    Uses Kahn's topological sort algorithm (BFS-based) which is O(V+E) and
    provably correct for all graph shapes including 3+ hop dependency chains.
    The previous DFS implementation prematurely discarded the ``on_stack`` set
    in its iterative loop, causing it to miss cycles reachable via multiple
    paths.

    Algorithm:
        1. Compute in-degree for every node.
        2. Enqueue all nodes with in-degree 0 (sources).
        3. Process the queue: for each dequeued node, decrement the in-degree
           of its neighbours; re-enqueue neighbours whose in-degree drops to 0.
        4. After the queue empties, any node with in-degree > 0 belongs to a
           cycle (Kahn's invariant: a DAG yields |V| processed nodes; a cyclic
           graph yields fewer).

    When a cycle is detected the function returns a short witness path that
    traverses one cycle: it performs a targeted DFS from one of the surviving
    high-in-degree nodes, following only edges that stay within the cycle
    residual subgraph, until a node is revisited.

    Args:
        graph: Adjacency list mapping each node to its neighbours.  Nodes
            present as neighbours but absent as keys are treated as sinks
            (in-degree counted, out-degree zero).

    Returns:
        A list of node names forming a cycle (first node == last node for
        clarity), or ``None`` if the graph is acyclic.
    """
    # Collect all nodes (keys + any neighbours not themselves keys).
    all_nodes: set[str] = set(graph)
    for neighbours in graph.values():
        all_nodes.update(neighbours)

    # Build in-degree table.
    in_degree: dict[str, int] = dict.fromkeys(all_nodes, 0)
    for node, neighbours in graph.items():
        for nbr in neighbours:
            in_degree[nbr] = in_degree.get(nbr, 0) + 1

    # BFS queue seeded with zero-in-degree nodes.
    queue: deque[str] = deque(n for n in all_nodes if in_degree[n] == 0)
    processed: int = 0

    while queue:
        node = queue.popleft()
        processed += 1
        for nbr in graph.get(node, []):
            in_degree[nbr] -= 1
            if in_degree[nbr] == 0:
                queue.append(nbr)

    if processed == len(all_nodes):
        # All nodes processed → graph is a DAG.
        return None

    # Cycle exists: collect the residual subgraph (nodes with in_degree > 0).
    # Walk one cycle starting from an arbitrary residual node using a path-aware DFS.
    residual: set[str] = {n for n in all_nodes if in_degree[n] > 0}

    # Recursive-style path tracking: stack carries (node, path_so_far).
    # We use a fresh visited set per DFS root so cross-path contamination cannot
    # produce a false cycle_start index.
    start = next(iter(residual))
    stack: list[tuple[str, list[str]]] = [(start, [start])]
    while stack:
        node, current_path = stack.pop()
        # If this node already appears in the current path we've closed a cycle.
        if node in current_path[:-1]:
            idx = current_path.index(node)
            # Slice from first occurrence to the repeated occurrence (inclusive).
            return current_path[idx:]
        if node not in residual:
            continue
        for nbr in graph.get(node, []):
            if nbr in residual:
                stack.append((nbr, [*current_path, nbr]))

    # Fallback: return any residual node list as evidence of a cycle.
    return list(residual)[:2]
