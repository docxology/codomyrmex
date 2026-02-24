"""Zero-Mock tests for DocumentWriter — uses real file I/O via tmp_path."""

import json
from pathlib import Path

import pytest

from codomyrmex.documents.core.document_writer import DocumentWriter, write_document
from codomyrmex.documents.exceptions import DocumentWriteError
from codomyrmex.documents.models.document import Document, DocumentFormat


@pytest.mark.unit
class TestDocumentWriter:
    """Test suite for DocumentWriter."""
    def setup_method(self):
        self.writer = DocumentWriter()

    def test_write_text(self, tmp_path):
        """Test writing a text document to a real file."""
        f = tmp_path / "test.txt"
        doc = Document("content", DocumentFormat.TEXT)

        self.writer.write(doc, str(f))

        assert f.exists()
        assert f.read_text(encoding="utf-8") == "content"

    def test_write_json(self, tmp_path):
        """Test writing a JSON document to a real file."""
        f = tmp_path / "test.json"
        doc = Document({"a": 1}, DocumentFormat.JSON)

        self.writer.write(doc, str(f))

        assert f.exists()
        written = json.loads(f.read_text(encoding="utf-8"))
        assert written == {"a": 1}

    def test_write_creates_parent_dirs(self, tmp_path):
        """Test that write creates parent directories."""
        f = tmp_path / "subdir" / "nested" / "test.txt"
        doc = Document("deep content", DocumentFormat.TEXT)

        self.writer.write(doc, str(f))

        assert f.exists()
        assert f.read_text(encoding="utf-8") == "deep content"

    def test_write_unsupported_format(self, tmp_path):
        """Test error for unsupported format."""
        f = tmp_path / "test.xml"
        doc = Document("content", DocumentFormat.XML)
        with pytest.raises(DocumentWriteError):
            self.writer.write(doc, str(f))


@pytest.mark.unit
class TestWriteDocumentConvenience:
    """Test suite for WriteDocumentConvenience."""
    def test_write_document_wrapper(self, tmp_path):
        """Test the convenience wrapper writes a real file."""
        f = tmp_path / "wrap.txt"
        doc = Document("content", DocumentFormat.TEXT)

        write_document(doc, str(f))

        assert f.exists()
        assert f.read_text(encoding="utf-8") == "content"
