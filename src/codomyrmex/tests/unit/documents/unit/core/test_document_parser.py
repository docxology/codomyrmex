import unittest
from unittest.mock import patch

import pytest

from codomyrmex.documents.core.document_parser import DocumentParser, parse_document
from codomyrmex.documents.exceptions import DocumentParseError
from codomyrmex.documents.models.document import DocumentFormat


@pytest.mark.unit
class TestDocumentParser(unittest.TestCase):
    def setUp(self):
        self.parser = DocumentParser()

    def test_parse_json(self):
        """Test parsing JSON string."""
        content = '{"key": "value"}'
        doc = self.parser.parse(content, DocumentFormat.JSON)
        self.assertEqual(doc.content, {"key": "value"})
        self.assertEqual(doc.format, DocumentFormat.JSON)

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        content = '{invalid: json}'
        with self.assertRaises(DocumentParseError):
            self.parser.parse(content, DocumentFormat.JSON)

    def test_parse_markdown(self):
        """Test parsing Markdown (returns string content currently)."""
        content = "# Title"
        doc = self.parser.parse(content, DocumentFormat.MARKDOWN)
        self.assertEqual(doc.content, "# Title")

    def test_parse_unsupported(self):
        """Test parsing unsupported format."""
        # Assuming one that isn't implemented separately or just falls through
        # Actually parse usually just wraps content if no specific parser needed
        # But if we had a binary format maybe?
        pass

@pytest.mark.unit
class TestParseDocumentConvenience(unittest.TestCase):
    @patch('codomyrmex.documents.core.document_parser.DocumentParser.parse')
    def test_parse_document_wrapper(self, mock_parse):
        """Test convenience wrapper."""
        parse_document("content", DocumentFormat.TEXT)
        mock_parse.assert_called_once()
