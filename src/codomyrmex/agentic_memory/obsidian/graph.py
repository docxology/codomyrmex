"""Obsidian vault link graph — build, query, analyse.

Uses a directed graph (dict-of-sets) so we have zero dependency on
``networkx`` in core.  The returned object duck-types the subset of the
``networkx.DiGraph`` API used by the tests.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.agentic_memory.obsidian.models import Note, Wikilink

# ── lightweight directed graph ───────────────────────────────────────


class _DiGraph:
    """Minimal directed graph matching part of the networkx API."""

    def __init__(self) -> None:
        self._adj: dict[str, set[str]] = {}

    def add_node(self, n: str) -> None:
        self._adj.setdefault(n, set())

    def add_edge(self, u: str, v: str) -> None:
        self._adj.setdefault(u, set()).add(v)
        self._adj.setdefault(v, set())

    def number_of_nodes(self) -> int:
        return len(self._adj)

    def number_of_edges(self) -> int:
        return sum(len(v) for v in self._adj.values())

    def is_directed(self) -> bool:
        return True

    def successors(self, n: str) -> list[str]:
        return list(self._adj.get(n, set()))

    def predecessors(self, n: str) -> list[str]:
        return [u for u, vs in self._adj.items() if n in vs]

    def nodes(self) -> list[str]:
        return list(self._adj.keys())

    def has_node(self, n: str) -> bool:
        return n in self._adj

    def has_edge(self, u: str, v: str) -> bool:
        return v in self._adj.get(u, set())

    def in_degree(self, n: str) -> int:
        """Number of edges pointing to *n*."""
        return len(self.predecessors(n))

    def out_degree(self, n: str) -> int:
        """Number of edges leaving *n*."""
        return len(self._adj.get(n, set()))

    def degree(self, n: str) -> int:
        """Total degree (in + out)."""
        return self.in_degree(n) + self.out_degree(n)


# ── public API ───────────────────────────────────────────────────────


def build_link_graph(vault: Any) -> _DiGraph:
    """Build a directed link graph from vault notes."""
    g = _DiGraph()
    for _rel, note in vault.notes.items():
        title = note.title
        g.add_node(title)
        for link in note.links:
            g.add_edge(title, link.target)
    return g


def get_backlinks(vault: Any, title: str) -> list[Note]:
    """Return notes that link *to* the given title."""
    results: list[Note] = []
    for _rel, note in vault.notes.items():
        if note.title == title:
            continue
        for link in note.links:
            if link.target == title:
                results.append(note)
                break
    return results


def get_forward_links(vault: Any, title: str) -> list[Note]:
    """Return notes linked *from* the given title."""
    note = vault.get_note(title)
    if note is None:
        return []
    results: list[Note] = []
    for link in note.links:
        target = vault.get_note(link.target)
        if target is not None:
            results.append(target)
    return results


def find_orphans(vault: Any) -> list[Note]:
    """Return notes with no inbound or outbound links."""
    g = build_link_graph(vault)
    orphans: list[Note] = []
    for _rel, note in vault.notes.items():
        title = note.title
        has_outgoing = len(g.successors(title)) > 0
        has_incoming = len(g.predecessors(title)) > 0
        if not has_outgoing and not has_incoming:
            orphans.append(note)
    return orphans


def find_dead_ends(vault: Any) -> list[Note]:
    """Return notes with no outgoing links (dead ends / leaf notes)."""
    g = build_link_graph(vault)
    dead_ends: list[Note] = []
    for _rel, note in vault.notes.items():
        if len(g.successors(note.title)) == 0 and len(g.predecessors(note.title)) > 0:
            dead_ends.append(note)
    return dead_ends


def find_hubs(vault: Any, *, min_links: int = 5) -> list[tuple[Note, int]]:
    """Return notes that are heavily linked (hub notes).

    Returns ``(note, total_degree)`` tuples sorted by degree descending.
    """
    g = build_link_graph(vault)
    hubs: list[tuple[Note, int]] = []
    for _rel, note in vault.notes.items():
        degree = g.degree(note.title)
        if degree >= min_links:
            hubs.append((note, degree))
    hubs.sort(key=lambda x: x[1], reverse=True)
    return hubs


def find_broken_links(vault: Any) -> list[tuple[Note, Wikilink]]:
    """Return ``(source_note, wikilink)`` pairs where the target note
    does not exist in the vault."""
    results: list[tuple[Note, Wikilink]] = []
    existing_titles = {n.title for n in vault.notes.values()}
    for _rel, note in vault.notes.items():
        for link in note.links:
            if link.target not in existing_titles:
                results.append((note, link))
    return results


def get_link_stats(vault: Any) -> dict[str, Any]:
    """Return summary statistics about the vault link graph."""
    g = build_link_graph(vault)
    n_nodes = g.number_of_nodes()
    n_edges = g.number_of_edges()
    max_possible = n_nodes * (n_nodes - 1) if n_nodes > 1 else 1
    density = n_edges / max_possible if max_possible > 0 else 0.0

    # Most linked (most incoming edges)
    incoming: dict[str, int] = {}
    for node in g.nodes():
        incoming[node] = len(g.predecessors(node))
    most_linked = sorted(incoming.items(), key=lambda x: x[1], reverse=True)[:5]

    # Top linkers (most outgoing edges)
    outgoing: dict[str, int] = {}
    for node in g.nodes():
        outgoing[node] = len(g.successors(node))
    top_linkers = sorted(outgoing.items(), key=lambda x: x[1], reverse=True)[:5]

    # Connected components (weakly connected, via BFS)
    visited: set[str] = set()
    components = 0
    for node in g.nodes():
        if node in visited:
            continue
        components += 1
        stack = [node]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(g.successors(current))
            stack.extend(g.predecessors(current))

    # Orphans and dead ends count
    orphan_count = sum(
        1 for n in g.nodes()
        if g.in_degree(n) == 0 and g.out_degree(n) == 0
    )
    dead_end_count = sum(
        1 for n in g.nodes()
        if g.out_degree(n) == 0 and g.in_degree(n) > 0
    )

    return {
        "node_count": n_nodes,
        "edge_count": n_edges,
        "density": round(density, 4),
        "components": components,
        "most_linked": most_linked,
        "top_linkers": top_linkers,
        "orphan_count": orphan_count,
        "dead_end_count": dead_end_count,
    }


def get_shortest_path(
    vault: Any,
    source: str,
    target: str,
) -> list[str] | None:
    """Find shortest path between two notes using BFS.

    Returns a list of note titles from source to target, or ``None``
    if no path exists.  Path is undirected (follows links both ways).
    """
    g = build_link_graph(vault)
    if not g.has_node(source) or not g.has_node(target):
        return None
    if source == target:
        return [source]

    visited: set[str] = {source}
    queue: list[list[str]] = [[source]]

    while queue:
        path = queue.pop(0)
        current = path[-1]
        neighbors = set(g.successors(current)) | set(g.predecessors(current))
        for neighbor in neighbors:
            if neighbor == target:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None
