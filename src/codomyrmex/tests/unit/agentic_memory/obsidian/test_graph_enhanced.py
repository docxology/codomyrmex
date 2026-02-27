"""Tests for enhanced graph features.

Tests for find_dead_ends, find_hubs, get_shortest_path,
in_degree/out_degree/degree, orphan/dead_end counts in stats,
and enhanced _DiGraph methods.
"""

from codomyrmex.agentic_memory.obsidian.graph import (
    build_link_graph,
    find_dead_ends,
    find_hubs,
    get_link_stats,
    get_shortest_path,
)
from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault


class TestDiGraphEnhanced:
    def test_has_node(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        g = build_link_graph(vault)
        assert g.has_node("My Test Note") is True
        assert g.has_node("Nonexistent XYZ") is False

    def test_has_edge(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        g = build_link_graph(vault)
        # Simple Note links to My Test Note
        assert g.has_edge("Simple Note", "My Test Note") is True

    def test_in_degree(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        g = build_link_graph(vault)
        # My Test Note should have at least 1 incoming link
        assert g.in_degree("My Test Note") >= 1

    def test_out_degree(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        g = build_link_graph(vault)
        # My Test Note links to several targets
        assert g.out_degree("My Test Note") >= 4

    def test_degree(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        g = build_link_graph(vault)
        d = g.degree("My Test Note")
        assert d == g.in_degree("My Test Note") + g.out_degree("My Test Note")


class TestFindDeadEnds:
    def test_dead_ends(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        dead_ends = find_dead_ends(vault)
        # Dead ends have incoming links but no outgoing links
        for note in dead_ends:
            g = build_link_graph(vault)
            assert g.out_degree(note.title) == 0
            assert g.in_degree(note.title) > 0


class TestFindHubs:
    def test_find_hubs_default(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        hubs = find_hubs(vault, min_links=3)
        # My Test Note has many links, should be a hub
        if hubs:
            assert hubs[0][1] >= 3  # degree >= min_links

    def test_find_hubs_sorted(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        hubs = find_hubs(vault, min_links=1)
        # Should be sorted by degree descending
        degrees = [d for _, d in hubs]
        assert degrees == sorted(degrees, reverse=True)


class TestShortestPath:
    def test_direct_path(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        path = get_shortest_path(vault, "Simple Note", "My Test Note")
        assert path is not None
        assert path[0] == "Simple Note"
        assert path[-1] == "My Test Note"

    def test_self_path(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        path = get_shortest_path(vault, "My Test Note", "My Test Note")
        assert path == ["My Test Note"]

    def test_nonexistent_source(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        path = get_shortest_path(vault, "ZZZZZ", "My Test Note")
        assert path is None


class TestLinkStatsEnhanced:
    def test_stats_include_orphan_count(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        stats = get_link_stats(vault)
        assert "orphan_count" in stats
        assert "dead_end_count" in stats
        assert isinstance(stats["orphan_count"], int)
        assert isinstance(stats["dead_end_count"], int)
