"""Tests for enhanced CRUD operations.

Tests for append_note, prepend_note, move_note, read_note_raw,
create_note with overwrite/template, remove_frontmatter_key.
"""

import pytest

from codomyrmex.agentic_memory.obsidian.crud import (
    append_note,
    create_note,
    move_note,
    prepend_note,
    read_note_raw,
    remove_frontmatter_key,
)
from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault


class TestAppendNote:
    def test_append_basic(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        note = append_note(vault, "Simple Note", "Added text")
        assert "Added text" in note.content

    def test_append_newline(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        raw = (tmp_vault / "Simple Note.md").read_text()
        append_note(vault, "Simple Note", "New line", newline=True)
        updated = (tmp_vault / "Simple Note.md").read_text()
        assert "New line" in updated

    def test_append_not_found(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileNotFoundError):
            append_note(vault, "Nonexistent", "text")


class TestPrependNote:
    def test_prepend_after_frontmatter(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        note = prepend_note(vault, "My Test Note", "PREPENDED TEXT", after_frontmatter=True)
        raw = (tmp_vault / "My Test Note.md").read_text()
        # PREPENDED TEXT should appear after --- but before original content
        fm_end = raw.find("---\n", 4) + 4
        after_fm = raw[fm_end:]
        assert after_fm.startswith("PREPENDED TEXT")

    def test_prepend_at_start(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        prepend_note(vault, "No Frontmatter", "TOP LINE", after_frontmatter=False)
        raw = (tmp_vault / "No Frontmatter.md").read_text()
        assert raw.startswith("TOP LINE")


class TestMoveNote:
    def test_move_to_folder(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        note = move_note(vault, "Simple Note", to="subfolder/")
        assert note.path is not None
        assert "subfolder" in str(note.path)
        assert not (tmp_vault / "Simple Note.md").exists()
        assert (tmp_vault / "subfolder" / "Simple Note.md").exists()

    def test_move_with_rename(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        note = move_note(vault, "No Frontmatter", to="subfolder/Renamed Note")
        assert note.title == "Renamed Note"

    def test_move_not_found(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileNotFoundError):
            move_note(vault, "Nonexistent", to="subfolder/")


class TestCreateNoteEnhanced:
    def test_create_with_overwrite(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # First create should work
        note = create_note(vault, "Overwrite Test", content="Original")
        # Overwrite should succeed
        note2 = create_note(vault, "Overwrite Test", content="Replaced", overwrite=True)
        assert "Replaced" in note2.content

    def test_create_without_overwrite_fails(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        create_note(vault, "Unique Note", content="First")
        with pytest.raises(FileExistsError):
            create_note(vault, "Unique Note", content="Second")

    def test_create_with_template(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # Templates/Daily.md exists in the vault
        note = create_note(vault, "From Template", template="Templates/Daily")
        # Should pick up the template content
        assert len(note.content) > 0


class TestReadNoteRaw:
    def test_read_raw(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        raw = read_note_raw(vault, "Simple Note")
        assert "# Simple Note" in raw
        assert isinstance(raw, str)

    def test_read_raw_not_found(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        with pytest.raises(FileNotFoundError):
            read_note_raw(vault, "Nonexistent")


class TestRemoveFrontmatterKey:
    def test_remove_key(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        note = remove_frontmatter_key(vault, "My Test Note", "status")
        assert "status" not in note.frontmatter

    def test_remove_nonexistent_key(self, tmp_vault):
        vault = ObsidianVault(tmp_vault)
        # Should not raise, just no-op
        note = remove_frontmatter_key(vault, "My Test Note", "nonexistent_key")
        assert "nonexistent_key" not in note.frontmatter
