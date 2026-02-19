"""Tests for Obsidian link graph analysis."""

import pytest

from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault
from codomyrmex.agentic_memory.obsidian.graph import (
    build_link_graph,
    find_broken_links,
    find_orphans,
    get_backlinks,
    get_forward_links,
    get_link_stats,
)


class TestBuildLinkGraph:
    def test_graph_has_nodes(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        graph = build_link_graph(vault)
        # 4 real notes + link targets added as edge destinations
        assert graph.number_of_nodes() >= 4

    def test_graph_has_edges(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        graph = build_link_graph(vault)
        assert graph.number_of_edges() > 0

    def test_graph_is_directed(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        graph = build_link_graph(vault)
        assert graph.is_directed()


class TestBacklinks:
    def test_backlinks_found(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # Simple Note links to My Test Note
        backlinks = get_backlinks(vault, "My Test Note")
        titles = [n.title for n in backlinks]
        assert "Simple Note" in titles

    def test_backlinks_none(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        backlinks = get_backlinks(vault, "Nested Note")
        # No notes link to Nested Note
        assert len(backlinks) == 0

    def test_backlinks_not_found(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        backlinks = get_backlinks(vault, "Nonexistent")
        assert len(backlinks) == 0


class TestForwardLinks:
    def test_forward_links(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # Simple Note links to My Test Note
        forward = get_forward_links(vault, "Simple Note")
        titles = [n.title for n in forward]
        assert "My Test Note" in titles


class TestOrphans:
    def test_finds_orphans(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        orphans = find_orphans(vault)
        # Nested Note has no links in or out
        titles = [n.title for n in orphans]
        assert "Nested Note" in titles


class TestBrokenLinks:
    def test_finds_broken(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        broken = find_broken_links(vault)
        # My Test Note links to "Another Note", "Target", "Some Note", "Other"
        # None of which exist
        assert len(broken) > 0
        targets = [link.target for _, link in broken]
        assert "Another Note" in targets

    def test_valid_links_not_broken(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        broken = find_broken_links(vault)
        # "My Test Note" is a valid target, should not appear as broken
        targets = [link.target for _, link in broken]
        assert "My Test Note" not in targets


class TestLinkStats:
    def test_stats_structure(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        stats = get_link_stats(vault)
        assert "node_count" in stats
        assert "edge_count" in stats
        assert "components" in stats
        assert "density" in stats
        assert "most_linked" in stats
        assert "top_linkers" in stats

    def test_stats_values(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        stats = get_link_stats(vault)
        assert stats["node_count"] >= 4  # Real notes + link targets
        assert stats["edge_count"] > 0
