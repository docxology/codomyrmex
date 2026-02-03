import pytest

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from codomyrmex.documents.core.document_writer import DocumentWriter, write_document
from codomyrmex.documents.models.document import Document, DocumentFormat
from codomyrmex.documents.exceptions import DocumentWriteError, UnsupportedFormatError

@pytest.mark.unit
class TestDocumentWriter(unittest.TestCase):
    def setUp(self):
        self.writer = DocumentWriter()
        self.doc = Document("content", DocumentFormat.TEXT)

    @patch('pathlib.Path.parent')
    def test_write_file_creation_error(self, mock_parent):
        """Test error when creating directory fails."""
        # Use a real path for this test to trigger logic, but mock mkdir
        path = Path("some/dir/file.txt")
        # We need mock_parent to be what path.parent returns, which is a bit tricky with PropertyMock
        # Easier to mock the mkdir call on the Path object that is created inside write
        
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            with self.assertRaises(DocumentWriteError):
                self.writer.write(self.doc, path)


    @patch('codomyrmex.documents.formats.text_handler.write_text')
    @patch('codomyrmex.documents.metadata.manager.update_metadata')
    def test_write_text(self, mock_update_meta, mock_write_text):
        """Test writing a text document."""
        self.writer.write(self.doc, "test.txt")
        mock_write_text.assert_called_once()
    
    @patch('codomyrmex.documents.formats.json_handler.write_json')
    def test_write_json(self, mock_write_json):
        """Test writing a JSON document."""
        doc = Document({"a": 1}, DocumentFormat.JSON)
        self.writer.write(doc, "test.json")
        mock_write_json.assert_called_once()

    def test_write_unsupported_format(self):
        """Test error for unsupported format."""
        doc = Document("content", DocumentFormat.XML)
        # XML is ostensibly not implemented in writer yet, raising UnsupportedFormatError wrapped in DocumentWriteError
        with self.assertRaises(DocumentWriteError):
            self.writer.write(doc, "test.xml")

@pytest.mark.unit
class TestWriteDocumentConvenience(unittest.TestCase):
    @patch('codomyrmex.documents.core.document_writer.DocumentWriter.write')
    def test_write_document_wrapper(self, mock_write):
        """Test the convenient wrapper."""
        doc = Document("content", DocumentFormat.TEXT)
        write_document(doc, "test.txt")
        mock_write.assert_called_once()
