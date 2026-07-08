"""Tests for bookmark CLI commands."""

import pytest

from codomyrmex.agentic_memory.obsidian.bookmarks import (
    BookmarkItem,
    _parse_bookmarks,
    bookmark_file,
    bookmark_folder,
    bookmark_search,
    bookmark_url,
    list_bookmarks,
)
from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable


class TestBookmarkItem:
    def test_create(self):
        b = BookmarkItem(title="My Note", path="notes/My Note.md")
        assert b.title == "My Note"
        assert b.type == "file"

    def test_defaults(self):
        b = BookmarkItem(title="Test")
        assert b.path == ""


class TestParseBookmarks:
    def test_tab_separated(self):
        lines = ["My Note\tnotes/My Note.md", "Folder\tfolder/"]
        bookmarks = _parse_bookmarks(lines)
        assert len(bookmarks) == 2
        assert bookmarks[0].path == "notes/My Note.md"

    def test_single_column(self):
        bookmarks = _parse_bookmarks(["My Note.md"])
        assert len(bookmarks) == 1

    def test_empty_lines(self):
        bookmarks = _parse_bookmarks(["Bookmark 1", "", "Bookmark 2"])
        assert len(bookmarks) == 2


class TestBookmarkUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_bookmarks(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_bookmarks(self._cli())

    def test_list_bookmarks_flags(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_bookmarks(self._cli(), total=True, verbose=True, format="json")

    def test_bookmark_file(self):
        with pytest.raises(ObsidianCLINotAvailable):
            bookmark_file(self._cli(), file="note")

    def test_bookmark_folder(self):
        with pytest.raises(ObsidianCLINotAvailable):
            bookmark_folder(self._cli(), "folder/")

    def test_bookmark_search(self):
        with pytest.raises(ObsidianCLINotAvailable):
            bookmark_search(self._cli(), "my query")

    def test_bookmark_url(self):
        with pytest.raises(ObsidianCLINotAvailable):
            bookmark_url(self._cli(), "https://example.com", title="Example")
