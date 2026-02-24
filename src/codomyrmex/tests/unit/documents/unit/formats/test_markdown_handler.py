"""Zero-Mock tests for Markdown handler — uses real file I/O via tmp_path."""

import pytest

from codomyrmex.documents.formats.markdown_handler import read_markdown, write_markdown


@pytest.mark.unit
class TestMarkdownHandler:
    """Test suite for MarkdownHandler."""
    def test_read_markdown(self, tmp_path):
        """Test reading markdown from a real file."""
        f = tmp_path / "test.md"
        f.write_text("# Header\nContent", encoding="utf-8")

        content = read_markdown(str(f))
        assert content == "# Header\nContent"

    def test_write_markdown(self, tmp_path):
        """Test writing markdown to a real file."""
        f = tmp_path / "test.md"
        content = "# Header\nContent"

        write_markdown(content, str(f))

        assert f.exists()
        assert f.read_text(encoding="utf-8") == content

    def test_roundtrip(self, tmp_path):
        """Test markdown write then read roundtrip."""
        f = tmp_path / "roundtrip.md"
        original = "# Title\n\n## Section\n\n- Item 1\n- Item 2"

        write_markdown(original, str(f))
        result = read_markdown(str(f))

        assert result == original
