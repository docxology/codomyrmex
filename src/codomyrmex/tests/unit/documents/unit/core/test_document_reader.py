"""Zero-Mock tests for DocumentReader — uses real file I/O via tmp_path."""


import pytest

from codomyrmex.documents.core.document_reader import DocumentReader, read_document
from codomyrmex.documents.exceptions import DocumentReadError
from codomyrmex.documents.models.document import DocumentFormat


@pytest.mark.unit
class TestDocumentReader:
    """Test suite for DocumentReader."""
    def setup_method(self):
        self.reader = DocumentReader()

    def test_read_file_not_found(self):
        """Test error when file does not exist."""
        with pytest.raises(DocumentReadError):
            self.reader.read("/tmp/nonexistent_file_xyz_12345.txt")

    def test_read_text_file(self, tmp_path):
        """Test reading a real text file."""
        f = tmp_path / "test.txt"
        f.write_text("file content", encoding="utf-8")

        doc = self.reader.read(str(f))

        assert doc.content == "file content"
        assert doc.format == DocumentFormat.TEXT

    def test_read_json_file(self, tmp_path):
        """Test reading a real JSON file with explicit format."""
        f = tmp_path / "test.json"
        f.write_text('{"a": 1}', encoding="utf-8")

        doc = self.reader.read(str(f), format=DocumentFormat.JSON)

        assert doc.content == {"a": 1}
        assert doc.format == DocumentFormat.JSON

    def test_read_markdown_file(self, tmp_path):
        """Test reading a real markdown file."""
        f = tmp_path / "test.md"
        f.write_text("# Title\n\nParagraph", encoding="utf-8")

        doc = self.reader.read(str(f))

        assert "# Title" in doc.content

    def test_detect_format_json(self, tmp_path):
        """Test format detection for JSON extension."""
        f = tmp_path / "data.json"
        f.write_text('{"x": 1}', encoding="utf-8")

        doc = self.reader.read(str(f))
        assert doc.format == DocumentFormat.JSON


@pytest.mark.unit
class TestReadDocumentConvenience:
    """Test suite for ReadDocumentConvenience."""
    def test_read_document_wrapper(self, tmp_path):
        """Test the convenience wrapper returns a real document."""
        f = tmp_path / "test.txt"
        f.write_text("hello", encoding="utf-8")

        doc = read_document(str(f))
        assert doc is not None
        assert doc.content == "hello"
