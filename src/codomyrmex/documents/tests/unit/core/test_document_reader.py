
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from codomyrmex.documents.core.document_reader import DocumentReader, read_document
from codomyrmex.documents.models.document import DocumentFormat
from codomyrmex.documents.exceptions import DocumentReadError, UnsupportedFormatError

class TestDocumentReader(unittest.TestCase):
    def setUp(self):
        self.reader = DocumentReader()

    @patch('pathlib.Path.exists')
    def test_read_file_not_found(self, mock_exists):
        """Test error when file does not exist."""
        mock_exists.return_value = False
        with self.assertRaises(DocumentReadError):
            self.reader.read("nonexistent.txt")

    @patch('pathlib.Path.exists')
    @patch('codomyrmex.documents.core.document_reader.DocumentReader._detect_format')
    @patch('codomyrmex.documents.core.document_reader.detect_encoding')
    @patch('codomyrmex.documents.formats.text_handler.read_text')
    @patch('codomyrmex.documents.metadata.extractor.extract_metadata')
    def test_read_text_auto_detect(self, mock_extract, mock_read_text, mock_encoding, mock_detect_format, mock_exists):
        """Test reading a text file with auto detection."""
        mock_exists.return_value = True
        mock_detect_format.return_value = DocumentFormat.TEXT
        mock_encoding.return_value = "utf-8"
        mock_read_text.return_value = "file content"
        mock_extract.return_value = {}

        doc = self.reader.read("test.txt")

        self.assertEqual(doc.content, "file content")
        self.assertEqual(doc.format, DocumentFormat.TEXT)
        self.assertEqual(doc.encoding, "utf-8")
        
        mock_read_text.assert_called_once()

    @patch('pathlib.Path.exists')
    @patch('codomyrmex.documents.formats.json_handler.read_json')
    @patch('codomyrmex.documents.metadata.extractor.extract_metadata')
    def test_read_json_explicit_format(self, mock_extract, mock_read_json, mock_exists):
        """Test reading a JSON file with explicit format."""
        mock_exists.return_value = True
        mock_read_json.return_value = {"a": 1}
        mock_extract.return_value = {}

        doc = self.reader.read("test.json", format=DocumentFormat.JSON)

        self.assertEqual(doc.content, {"a": 1})
        self.assertEqual(doc.format, DocumentFormat.JSON)
        mock_read_json.assert_called_once()


    @patch('pathlib.Path.exists')
    def test_read_unsupported_format(self, mock_exists):
        """Test error for unsupported format."""
        mock_exists.return_value = True
        # It handles MARKDOWN, JSON, YAML, PDF, TEXT. 
        # So XML should raise UnsupportedFormatError wrapped in DocumentReadError
        with self.assertRaises(DocumentReadError):
            self.reader.read("test.xml", format=DocumentFormat.XML)

    def test_detect_format(self):
        """Test format detection logic."""
        # This relies on mime_type_detector, but we can verify mapping logic
        # We might need to mock detect_format_from_path
        with patch('codomyrmex.documents.core.document_reader.detect_format_from_path') as mock_detect:
            mock_detect.return_value = "json"
            fmt = self.reader._detect_format(Path("test.json"))
            self.assertEqual(fmt, DocumentFormat.JSON)
            
            mock_detect.return_value = "markdown"
            fmt = self.reader._detect_format(Path("test.md"))
            self.assertEqual(fmt, DocumentFormat.MARKDOWN)

class TestReadDocumentConvenience(unittest.TestCase):
    @patch('codomyrmex.documents.core.document_reader.DocumentReader.read')
    def test_read_document_wrapper(self, mock_read):
        """Test the convenience wrapper function."""
        read_document("test.txt")
        mock_read.assert_called_once()
