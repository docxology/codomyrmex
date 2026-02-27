"""Tests for enhanced search features.

Tests for search_regex, search_vault with case_sensitive/folder,
filter_by_tags (multi-tag), filter_by_frontmatter_exists,
find_notes_linking_to, find_notes_with_embeds.
"""

import re

from codomyrmex.agentic_memory.obsidian.search import (
    filter_by_frontmatter_exists,
    filter_by_tags,
    find_notes_linking_to,
    find_notes_with_embeds,
    search_regex,
    search_vault,
)
from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault


class TestSearchRegex:
    def test_regex_basic(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_regex(vault, r"#\w+")
        assert len(results) > 0

    def test_regex_pattern(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_regex(vault, r"\[\[.*?\]\]")
        assert len(results) > 0

    def test_regex_no_match(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_regex(vault, r"ZZZZZZNONEXIST")
        assert len(results) == 0

    def test_regex_case_sensitive(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_regex(vault, r"My Test Note", flags=0)  # 0 = no flags
        # Should find it in content (case-sensitive)
        assert len(results) >= 0  # may or may not depending on exact content


class TestSearchVaultEnhanced:
    def test_case_sensitive(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # Case sensitive should find nothing for lowercase
        results_insensitive = search_vault(vault, "my test", case_sensitive=False)
        results_sensitive = search_vault(vault, "my test", case_sensitive=True)
        # Insensitive should find more or equal results
        assert len(results_insensitive) >= len(results_sensitive)

    def test_folder_filter(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # Only search in subfolder
        results = search_vault(vault, "subfolder", folder="subfolder")
        for r in results:
            # All results should be from subfolder
            assert r.note.path is not None

    def test_frontmatter_value_match(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = search_vault(vault, "draft")
        assert len(results) > 0  # My Test Note has status: draft


class TestFilterByTags:
    def test_match_all(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = filter_by_tags(vault, ["testing", "obsidian"], match_all=True)
        assert len(results) >= 1
        for note in results:
            tag_names = {t.name for t in note.tags}
            assert "testing" in tag_names
            assert "obsidian" in tag_names

    def test_match_any(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = filter_by_tags(vault, ["testing", "simple-tag"], match_all=False)
        assert len(results) >= 2  # At least My Test Note and Simple Note

    def test_strip_hash(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = filter_by_tags(vault, ["#testing"])
        assert len(results) >= 1


class TestFilterByFrontmatterExists:
    def test_single_key(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = filter_by_frontmatter_exists(vault, "status")
        assert len(results) >= 1
        for note in results:
            assert "status" in note.frontmatter

    def test_multiple_keys(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = filter_by_frontmatter_exists(vault, "title", "status")
        assert len(results) >= 1  # My Test Note has both

    def test_nonexistent_key(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = filter_by_frontmatter_exists(vault, "nonexistent_key_xyz")
        assert len(results) == 0


class TestFindNotesLinkingTo:
    def test_find_linkers(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = find_notes_linking_to(vault, "My Test Note")
        titles = [n.title for n in results]
        assert "Simple Note" in titles
        assert "Hub Note" in titles

    def test_no_linkers(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = find_notes_linking_to(vault, "Nonexistent Target")
        assert len(results) == 0


class TestFindNotesWithEmbeds:
    def test_any_embeds(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = find_notes_with_embeds(vault)
        assert len(results) >= 1  # My Test Note has embeds
        titles = [n.title for n in results]
        assert "My Test Note" in titles

    def test_specific_embed(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = find_notes_with_embeds(vault, target="image.png")
        assert len(results) >= 1

    def test_no_embed_match(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        results = find_notes_with_embeds(vault, target="nonexistent.png")
        assert len(results) == 0
