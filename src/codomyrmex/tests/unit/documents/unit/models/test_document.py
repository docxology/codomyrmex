import unittest
from datetime import datetime

import pytest

from codomyrmex.documents.models.document import Document, DocumentFormat, DocumentType


@pytest.mark.unit
class TestDocument(unittest.TestCase):
    """Test suite for Document."""
    def test_document_initialization(self):
        """Test basic document initialization."""
        content = "Test content"
        fmt = DocumentFormat.TEXT
        doc = Document(content=content, format=fmt)

        self.assertEqual(doc.content, content)
        self.assertEqual(doc.format, fmt)
        self.assertIsNone(doc.file_path)
        self.assertIsInstance(doc.created_at, datetime)
        self.assertIsInstance(doc.modified_at, datetime)
        self.assertEqual(doc.metadata, {})

    def test_document_type_property(self):
        """Test document type derivation from format."""
        # Text
        doc = Document("content", DocumentFormat.TEXT)
        self.assertEqual(doc.type, DocumentType.TEXT)

        # Structure
        doc = Document("content", DocumentFormat.JSON)
        self.assertEqual(doc.type, DocumentType.STRUCTURED)

        # Markup
        doc = Document("content", DocumentFormat.MARKDOWN)
        self.assertEqual(doc.type, DocumentType.MARKUP)

        # Binary
        doc = Document("content", DocumentFormat.PDF)
        self.assertEqual(doc.type, DocumentType.BINARY)

    def test_get_content_as_string_string_content(self):
        """Test getting content when already a string."""
        doc = Document("hello", DocumentFormat.TEXT)
        self.assertEqual(doc.get_content_as_string(), "hello")

    def test_get_content_as_string_dict_content(self):
        """Test getting content when dict (JSON)."""
        data = {"key": "value"}
        doc = Document(data, DocumentFormat.JSON)
        content_str = doc.get_content_as_string()
        self.assertIn('"key": "value"', content_str)

    def test_get_content_as_string_bytes_content(self):
        """Test getting content when bytes."""
        data = b"hello bytes"
        doc = Document(data, DocumentFormat.TEXT, encoding="utf-8")
        self.assertEqual(doc.get_content_as_string(), "hello bytes")

    def test_metadata_defaults(self):
        """Test that metadata defaults to empty dict."""
        doc = Document("content", DocumentFormat.TEXT)
        self.assertEqual(doc.metadata, {})

        doc_with_meta = Document("content", DocumentFormat.TEXT, metadata={"author": "me"})
        self.assertEqual(doc_with_meta.metadata, {"author": "me"})
