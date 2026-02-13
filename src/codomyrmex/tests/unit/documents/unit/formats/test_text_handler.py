"""Zero-Mock tests for text handler — uses real file I/O via tmp_path."""

import pytest

from codomyrmex.documents.formats.text_handler import read_text, write_text


@pytest.mark.unit
class TestTextHandler:
    def test_read_text(self, tmp_path):
        """Test reading plain text from a real file."""
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")

        content = read_text(str(f))
        assert content == "hello world"

    def test_write_text(self, tmp_path):
        """Test writing plain text to a real file."""
        f = tmp_path / "test.txt"

        write_text("content", str(f))

        assert f.exists()
        assert f.read_text(encoding="utf-8") == "content"

    def test_roundtrip(self, tmp_path):
        """Test text write then read roundtrip."""
        f = tmp_path / "roundtrip.txt"
        original = "Line 1\nLine 2\nLine 3"

        write_text(original, str(f))
        result = read_text(str(f))

        assert result == original
