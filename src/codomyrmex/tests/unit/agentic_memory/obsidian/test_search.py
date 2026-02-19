"""Tests for Obsidian vault search and filtering."""

import pytest

from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault
from codomyrmex.agentic_memory.obsidian.search import (
    filter_by_date,
    filter_by_frontmatter,
    filter_by_tag,
    search_vault,
)


class TestSearchVault:
    def test_search_by_content(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "simple note")
        assert len(results) > 0
        titles = [r.note.title for r in results]
        assert "Simple Note" in titles

    def test_search_by_title(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "Nested")
        assert len(results) > 0
        assert any(r.match_type == "title" for r in results)

    def test_search_empty_query(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "")
        assert len(results) == 0

    def test_search_no_match(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "zzzzzznonexistentzzzzzz")
        assert len(results) == 0

    def test_search_limit(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "note", limit=2)
        assert len(results) <= 2

    def test_search_has_context(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "wikilink")
        # Even if no results for "wikilink", test structure
        # Search for something that exists
        results = search_vault(vault, "subfolder")
        if results:
            assert results[0].context != ""

    def test_search_scores_descending(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "note")
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score


class TestFilterByTag:
    def test_filter_exact(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_tag(vault, "testing")
        assert len(notes) > 0

    def test_filter_nested_included(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_tag(vault, "parent", include_nested=True)
        # "parent/child" tag should match "parent"
        assert len(notes) > 0

    def test_filter_nested_excluded(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_tag(vault, "parent", include_nested=False)
        # Exact match only - "parent" tag doesn't exist as exact
        assert len(notes) == 0

    def test_filter_no_match(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_tag(vault, "nonexistent-tag-xyz")
        assert len(notes) == 0

    def test_filter_strips_hash(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes1 = filter_by_tag(vault, "testing")
        notes2 = filter_by_tag(vault, "#testing")
        assert len(notes1) == len(notes2)


class TestFilterByFrontmatter:
    def test_filter_key_exists(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_frontmatter(vault, "title")
        assert len(notes) > 0

    def test_filter_key_value(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_frontmatter(vault, "status", "draft")
        assert len(notes) == 1
        assert notes[0].frontmatter["status"] == "draft"

    def test_filter_no_match(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_frontmatter(vault, "nonexistent_key")
        assert len(notes) == 0


class TestFilterByDate:
    def test_filter_after(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_date(vault, after="2024-01-01", date_field="created")
        assert len(notes) > 0

    def test_filter_before(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_date(vault, before="2025-01-01", date_field="created")
        assert len(notes) > 0

    def test_filter_no_date_field(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        notes = filter_by_date(vault, after="2020-01-01", date_field="nonexistent")
        assert len(notes) == 0
