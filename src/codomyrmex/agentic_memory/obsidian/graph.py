"""
Obsidian Link Graph Analysis.

Builds a directed graph of note interconnections using NetworkX.
Provides backlink analysis, orphan detection, and broken link finding.
"""

from __future__ import annotations

from typing import Any

import networkx as nx

from .models import Note, WikiLink
from .vault import ObsidianVault


def build_link_graph(vault: ObsidianVault) -> nx.DiGraph:
    """Build a directed graph from vault wikilinks.

    Nodes are note titles. Edges represent wikilinks from source to target.

    Args:
        vault: The Obsidian vault to analyze.

    Returns:
        NetworkX DiGraph with notes as nodes and links as edges.
    """
    graph = nx.DiGraph()

    # Add all notes as nodes
    for note in vault.notes.values():
        graph.add_node(note.title, path=str(note.path))

    # Add edges for wikilinks
    for note in vault.notes.values():
        for link in note.links:
            graph.add_edge(note.title, link.target)

    return graph


def get_backlinks(vault: ObsidianVault, path: str) -> list[Note]:
    """Find notes that link TO the given note.

    Args:
        vault: The Obsidian vault.
        path: Relative path or title of the target note.

    Returns:
        List of notes that contain wikilinks to the target.
    """
    target_note = vault.get_note(path)
    if target_note is None:
        return []

    target_title = target_note.title
    backlinks: list[Note] = []

    for note in vault.notes.values():
        if note.title == target_title:
            continue
        for link in note.links:
            if link.target == target_title:
                backlinks.append(note)
                break

    return backlinks


def get_forward_links(vault: ObsidianVault, path: str) -> list[Note]:
    """Find notes that the given note links TO.

    Args:
        vault: The Obsidian vault.
        path: Relative path or title of the source note.

    Returns:
        List of notes that the source links to (only existing notes).
    """
    source_note = vault.get_note(path)
    if source_note is None:
        return []

    forward: list[Note] = []
    for link in source_note.links:
        target = vault.get_note(link.target)
        if target is not None:
            forward.append(target)

    return forward


def find_orphans(vault: ObsidianVault) -> list[Note]:
    """Find notes with no inbound AND no outbound links.

    Returns:
        List of orphan notes.
    """
    graph = build_link_graph(vault)
    orphans: list[Note] = []

    for note in vault.notes.values():
        in_degree = graph.in_degree(note.title) if note.title in graph else 0
        out_degree = graph.out_degree(note.title) if note.title in graph else 0
        if in_degree == 0 and out_degree == 0:
            orphans.append(note)

    return orphans


def find_broken_links(vault: ObsidianVault) -> list[tuple[Note, WikiLink]]:
    """Find wikilinks that point to non-existent notes.

    Returns:
        List of (source_note, broken_wikilink) tuples.
    """
    note_titles = {n.title for n in vault.notes.values()}
    broken: list[tuple[Note, WikiLink]] = []

    for note in vault.notes.values():
        for link in note.links:
            # Check if target exists as a title or as a path
            if link.target not in note_titles:
                target_note = vault.get_note(link.target)
                if target_note is None:
                    broken.append((note, link))

    return broken


def get_link_stats(vault: ObsidianVault) -> dict[str, Any]:
    """Get link graph statistics.

    Returns:
        Dict with: node_count, edge_count, components, density,
        most_linked (top 5 most-linked-to notes),
        top_linkers (top 5 notes with most outbound links).
    """
    graph = build_link_graph(vault)

    # Most linked-to (highest in-degree)
    in_degrees = sorted(graph.in_degree(), key=lambda x: x[1], reverse=True)
    most_linked = [
        {"note": name, "inbound_links": deg}
        for name, deg in in_degrees[:5]
        if deg > 0
    ]

    # Top linkers (highest out-degree)
    out_degrees = sorted(graph.out_degree(), key=lambda x: x[1], reverse=True)
    top_linkers = [
        {"note": name, "outbound_links": deg}
        for name, deg in out_degrees[:5]
        if deg > 0
    ]

    # Connected components (treat as undirected for this)
    undirected = graph.to_undirected()
    components = nx.number_connected_components(undirected) if len(graph) > 0 else 0

    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "components": components,
        "density": nx.density(graph) if len(graph) > 1 else 0.0,
        "most_linked": most_linked,
        "top_linkers": top_linkers,
    }
