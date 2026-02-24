"""Tests for Obsidian vault management."""

import pytest

from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault


class TestObsidianVault:
    """Test suite for ObsidianVault."""
    def test_load_vault(self, tmp_vault):
        """Test functionality: load vault."""
        vault = ObsidianVault(tmp_vault)
        assert vault.path == tmp_vault.resolve()
        assert len(vault.notes) == 4  # 3 root + 1 nested

    def test_vault_not_found(self, tmp_path):
        """Test functionality: vault not found."""
        with pytest.raises(FileNotFoundError):
            ObsidianVault(tmp_path / "nonexistent")

    def test_vault_not_directory(self, tmp_path):
        """Test functionality: vault not directory."""
        f = tmp_path / "file.txt"
        f.write_text("not a dir")
        with pytest.raises(ValueError):
            ObsidianVault(f)

    def test_get_note_by_path(self, tmp_vault):
        """Test functionality: get note by path."""
        vault = ObsidianVault(tmp_vault)
        note = vault.get_note("My Test Note.md")
        assert note is not None
        assert note.title == "My Test Note"

    def test_get_note_by_title(self, tmp_vault):
        """Test functionality: get note by title."""
        vault = ObsidianVault(tmp_vault)
        note = vault.get_note("Simple Note")
        assert note is not None
        assert note.title == "Simple Note"

    def test_get_note_without_extension(self, tmp_vault):
        """Test functionality: get note without extension."""
        vault = ObsidianVault(tmp_vault)
        note = vault.get_note("My Test Note")
        assert note is not None

    def test_get_note_not_found(self, tmp_vault):
        """Test functionality: get note not found."""
        vault = ObsidianVault(tmp_vault)
        assert vault.get_note("Nonexistent") is None

    def test_metadata(self, tmp_vault):
        """Test functionality: metadata."""
        vault = ObsidianVault(tmp_vault)
        meta = vault.metadata
        assert meta.note_count == 4
        assert meta.tag_count > 0
        assert meta.link_count > 0

    def test_refresh(self, tmp_vault):
        """Test functionality: refresh."""
        vault = ObsidianVault(tmp_vault)
        _ = vault.notes  # Load cache
        (tmp_vault / "New Note.md").write_text("# New\nContent.")
        vault.refresh()
        assert len(vault.notes) == 5

    def test_excludes_dotfiles(self, tmp_vault):
        """Test functionality: excludes dotfiles."""
        vault = ObsidianVault(tmp_vault)
        # .obsidian/ files should not be in notes
        for path in vault.notes:
            assert ".obsidian" not in path

    def test_get_config(self, tmp_vault):
        """Test functionality: get config."""
        vault = ObsidianVault(tmp_vault)
        config = vault.get_config()
        assert "app" in config
        assert config["app"]["vimMode"] is False

    def test_get_all_tags(self, tmp_vault):
        """Test functionality: get all tags."""
        vault = ObsidianVault(tmp_vault)
        tags = vault.get_all_tags()
        assert len(tags) > 0
        # Should have frontmatter tags from sample note
        assert "testing" in tags or "obsidian" in tags

    def test_nested_note_found(self, tmp_vault):
        """Test functionality: nested note found."""
        vault = ObsidianVault(tmp_vault)
        # The nested note should be accessible
        found = False
        for path, note in vault.notes.items():
            if note.title == "Nested Note":
                found = True
                assert "subfolder" in path
        assert found
