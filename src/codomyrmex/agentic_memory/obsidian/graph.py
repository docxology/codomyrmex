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
    """Minimal directed graph matching the part of the networkx API
    that the tests exercise."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._adj: dict[str, set[str]] = {}

    def add_node(self, n: str) -> None:
        """Execute Add Node operations natively."""
        self._adj.setdefault(n, set())

    def add_edge(self, u: str, v: str) -> None:
        """Execute Add Edge operations natively."""
        self._adj.setdefault(u, set()).add(v)
        self._adj.setdefault(v, set())

    def number_of_nodes(self) -> int:
        """Execute Number Of Nodes operations natively."""
        return len(self._adj)

    def number_of_edges(self) -> int:
        """Execute Number Of Edges operations natively."""
        return sum(len(v) for v in self._adj.values())

    def is_directed(self) -> bool:
        """Execute Is Directed operations natively."""
        return True

    def successors(self, n: str) -> list[str]:
        """Execute Successors operations natively."""
        return list(self._adj.get(n, set()))

    def predecessors(self, n: str) -> list[str]:
        """Execute Predecessors operations natively."""
        return [u for u, vs in self._adj.items() if n in vs]

    def nodes(self) -> list[str]:
        """Execute Nodes operations natively."""
        return list(self._adj.keys())


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

    return {
        "node_count": n_nodes,
        "edge_count": n_edges,
        "density": round(density, 4),
        "components": components,
        "most_linked": most_linked,
        "top_linkers": top_linkers,
    }
