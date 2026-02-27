"""Tests for enhanced Obsidian vault features.

Tests for has_note, list_notes, list_folders, get_notes_by_tag,
alias lookup, dunder methods, metadata totals, and config readers.
"""

from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault


class TestVaultEnhancedLookup:
    def test_has_note(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        assert vault.has_note("My Test Note") is True
        assert vault.has_note("Nonexistent") is False

    def test_lookup_by_alias(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # My Test Note has aliases: ["Test Note", "TN"]
        note = vault.get_note("Test Note")
        assert note is not None
        assert note.title == "My Test Note"

    def test_lookup_by_alias_short(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        note = vault.get_note("TN")
        assert note is not None
        assert note.title == "My Test Note"

    def test_contains_operator(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        assert "My Test Note" in vault
        assert "Nonexistent" not in vault

    def test_len(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        assert len(vault) == 7

    def test_iter(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        titles = [n.title for n in vault]
        assert "My Test Note" in titles
        assert "Simple Note" in titles


class TestVaultEnhancedListing:
    def test_list_notes(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        all_notes = vault.list_notes()
        assert len(all_notes) == 7
        assert all(n.endswith(".md") for n in all_notes)

    def test_list_notes_folder(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        nested = vault.list_notes(folder="subfolder")
        assert len(nested) == 1
        assert "Nested Note.md" in nested[0]

    def test_list_folders(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        folders = vault.list_folders()
        assert "subfolder" in folders
        assert "daily" in folders
        assert "Templates" in folders

    def test_get_notes_by_tag(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        daily_notes = vault.get_notes_by_tag("daily")
        assert len(daily_notes) >= 1
        assert any(n.title == "2024-01-15" for n in daily_notes)


class TestVaultEnhancedMetadata:
    def test_metadata_includes_words(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        meta = vault.metadata
        assert meta.total_words > 0

    def test_metadata_includes_folders(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        meta = vault.metadata
        assert meta.folder_count >= 3  # subfolder, daily, Templates


class TestVaultConfig:
    def test_get_daily_notes_config(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        config = vault.get_daily_notes_config()
        assert config.get("folder") == "daily"
        assert config.get("format") == "YYYY-MM-DD"

    def test_repr(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        r = repr(vault)
        assert "ObsidianVault" in r
        assert "test-vault" in r
