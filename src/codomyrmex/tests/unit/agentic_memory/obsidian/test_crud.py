"""Tests for Obsidian note CRUD operations."""

import pytest

from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault
from codomyrmex.agentic_memory.obsidian.crud import (
    create_note,
    read_note,
    update_note,
    delete_note,
    get_frontmatter,
    set_frontmatter,
    rename_note,
)


class TestCreateNote:
    """Test suite for CreateNote."""
    def test_create_basic(self, tmp_vault):
        """Test functionality: create basic."""
        vault = ObsidianVault(tmp_vault)
        note = create_note(vault, "New Note.md", content="Hello world")
        assert note.title == "New Note"
        assert note.content == "Hello world"
        assert (tmp_vault / "New Note.md").exists()

    def test_create_with_frontmatter(self, tmp_vault):
        """Test functionality: create with frontmatter."""
        vault = ObsidianVault(tmp_vault)
        fm = {"title": "Created", "tags": ["auto"]}
        note = create_note(vault, "Created.md", content="Body", frontmatter=fm)
        assert note.frontmatter["title"] == "Created"

    def test_create_in_subfolder(self, tmp_vault):
        """Test functionality: create in subfolder."""
        vault = ObsidianVault(tmp_vault)
        note = create_note(vault, "deep/folder/Note.md", content="Deep")
        assert (tmp_vault / "deep" / "folder" / "Note.md").exists()

    def test_create_adds_md_extension(self, tmp_vault):
        """Test functionality: create adds md extension."""
        vault = ObsidianVault(tmp_vault)
        note = create_note(vault, "NoExt", content="Test")
        assert (tmp_vault / "NoExt.md").exists()

    def test_create_duplicate_raises(self, tmp_vault):
        """Test functionality: create duplicate raises."""
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileExistsError):
            create_note(vault, "My Test Note.md")

    def test_create_traversal_blocked(self, tmp_vault):
        """Test functionality: create traversal blocked."""
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(ValueError, match="traversal"):
            create_note(vault, "../../etc/passwd")


class TestReadNote:
    """Test suite for ReadNote."""
    def test_read_existing(self, tmp_vault):
        """Test functionality: read existing."""
        vault = ObsidianVault(tmp_vault)
        note = read_note(vault, "My Test Note.md")
        assert note.frontmatter["title"] == "My Test Note"
        assert len(note.links) > 0

    def test_read_not_found(self, tmp_vault):
        """Test functionality: read not found."""
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileNotFoundError):
            read_note(vault, "Nonexistent.md")

    def test_read_without_extension(self, tmp_vault):
        """Test functionality: read without extension."""
        vault = ObsidianVault(tmp_vault)
        note = read_note(vault, "Simple Note")
        assert note.title == "Simple Note"


class TestUpdateNote:
    """Test suite for UpdateNote."""
    def test_update_content(self, tmp_vault):
        """Test functionality: update content."""
        vault = ObsidianVault(tmp_vault)
        note = update_note(vault, "Simple Note.md", content="Updated content")
        # Re-read to verify
        note2 = read_note(vault, "Simple Note.md")
        assert "Updated content" in note2.content

    def test_update_frontmatter(self, tmp_vault):
        """Test functionality: update frontmatter."""
        vault = ObsidianVault(tmp_vault)
        note = update_note(
            vault, "My Test Note.md", frontmatter={"new_key": "new_value"}
        )
        note2 = read_note(vault, "My Test Note.md")
        assert note2.frontmatter["new_key"] == "new_value"
        # Original keys preserved
        assert note2.frontmatter["title"] == "My Test Note"

    def test_update_not_found(self, tmp_vault):
        """Test functionality: update not found."""
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileNotFoundError):
            update_note(vault, "Nonexistent.md", content="x")


class TestDeleteNote:
    """Test suite for DeleteNote."""
    def test_delete_existing(self, tmp_vault):
        """Test functionality: delete existing."""
        vault = ObsidianVault(tmp_vault)
        assert delete_note(vault, "Simple Note.md") is True
        assert not (tmp_vault / "Simple Note.md").exists()

    def test_delete_not_found(self, tmp_vault):
        """Test functionality: delete not found."""
        vault = ObsidianVault(tmp_vault)
        assert delete_note(vault, "Nonexistent.md") is False

    def test_delete_traversal_blocked(self, tmp_vault):
        """Test functionality: delete traversal blocked."""
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(ValueError, match="traversal"):
            delete_note(vault, "../../etc/passwd")


class TestFrontmatter:
    """Test suite for Frontmatter."""
    def test_get_frontmatter(self, tmp_vault):
        """Test functionality: get frontmatter."""
        vault = ObsidianVault(tmp_vault)
        fm = get_frontmatter(vault, "My Test Note.md")
        assert fm["title"] == "My Test Note"
        assert "testing" in fm["tags"]

    def test_set_frontmatter_merge(self, tmp_vault):
        """Test functionality: set frontmatter merge."""
        vault = ObsidianVault(tmp_vault)
        note = set_frontmatter(vault, "My Test Note.md", {"priority": "high"})
        fm = get_frontmatter(vault, "My Test Note.md")
        assert fm["priority"] == "high"
        assert fm["title"] == "My Test Note"  # Original preserved


class TestRenameNote:
    """Test suite for RenameNote."""
    def test_rename_basic(self, tmp_vault):
        """Test functionality: rename basic."""
        vault = ObsidianVault(tmp_vault)
        note = rename_note(vault, "Simple Note.md", "Renamed Note.md")
        assert note.title == "Renamed Note"
        assert not (tmp_vault / "Simple Note.md").exists()
        assert (tmp_vault / "Renamed Note.md").exists()

    def test_rename_updates_links(self, tmp_vault):
        """Test functionality: rename updates links."""
        vault = ObsidianVault(tmp_vault)
        # Simple Note links to My Test Note. Rename My Test Note.
        rename_note(vault, "My Test Note.md", "Renamed Test.md")
        # Check that Simple Note's content was updated
        content = (tmp_vault / "Simple Note.md").read_text()
        assert "[[Renamed Test]]" in content

    def test_rename_not_found(self, tmp_vault):
        """Test functionality: rename not found."""
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileNotFoundError):
            rename_note(vault, "Nonexistent.md", "New.md")

    def test_rename_target_exists(self, tmp_vault):
        """Test functionality: rename target exists."""
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileExistsError):
            rename_note(vault, "Simple Note.md", "My Test Note.md")
