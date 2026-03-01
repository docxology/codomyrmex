from datetime import datetime

import pytest

from codomyrmex.documents.models.document import Document, DocumentFormat, DocumentType


@pytest.mark.unit
class TestDocument:
    """Test suite for Document."""
    def test_document_initialization(self):
        """Test basic document initialization."""
        content = "Test content"
        fmt = DocumentFormat.TEXT
        doc = Document(content=content, format=fmt)

        assert doc.content == content
        assert doc.format == fmt
        assert doc.file_path is None
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.modified_at, datetime)
        assert doc.metadata == {}

    def test_document_type_property(self):
        """Test document type derivation from format."""
        # Text
        doc = Document("content", DocumentFormat.TEXT)
        assert doc.type == DocumentType.TEXT

        # Structure
        doc = Document("content", DocumentFormat.JSON)
        assert doc.type == DocumentType.STRUCTURED

        # Markup
        doc = Document("content", DocumentFormat.MARKDOWN)
        assert doc.type == DocumentType.MARKUP

        # Binary
        doc = Document("content", DocumentFormat.PDF)
        assert doc.type == DocumentType.BINARY

    def test_get_content_as_string_string_content(self):
        """Test getting content when already a string."""
        doc = Document("hello", DocumentFormat.TEXT)
        assert doc.get_content_as_string() == "hello"

    def test_get_content_as_string_dict_content(self):
        """Test getting content when dict (JSON)."""
        data = {"key": "value"}
        doc = Document(data, DocumentFormat.JSON)
        content_str = doc.get_content_as_string()
        assert '"key": "value"' in content_str

    def test_get_content_as_string_bytes_content(self):
        """Test getting content when bytes."""
        data = b"hello bytes"
        doc = Document(data, DocumentFormat.TEXT, encoding="utf-8")
        assert doc.get_content_as_string() == "hello bytes"

    def test_metadata_defaults(self):
        """Test that metadata defaults to empty dict."""
        doc = Document("content", DocumentFormat.TEXT)
        assert doc.metadata == {}

        doc_with_meta = Document("content", DocumentFormat.TEXT, metadata={"author": "me"})
        assert doc_with_meta.metadata == {"author": "me"}
