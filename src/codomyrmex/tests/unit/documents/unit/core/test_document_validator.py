import pytest

import unittest
from unittest.mock import patch, MagicMock
from codomyrmex.documents.core.document_validator import DocumentValidator, validate_document
from codomyrmex.documents.models.document import Document, DocumentFormat
from codomyrmex.documents.exceptions import DocumentValidationError

@pytest.mark.unit
class TestDocumentValidator(unittest.TestCase):
    def setUp(self):
        self.validator = DocumentValidator()

    def test_validate_structured_json(self):
        """Test validation of structured document against schema."""
        doc = Document({"age": 30}, DocumentFormat.JSON)
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer"}
            }
        }
        result = self.validator.validate(doc, schema=schema)
        self.assertTrue(result.is_valid)

    def test_validate_structured_json_fail(self):
        """Test validation failure."""
        doc = Document({"age": "thirty"}, DocumentFormat.JSON)
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer"}
            }
        }
        result = self.validator.validate(doc, schema=schema)
        self.assertFalse(result.is_valid)


    def test_validate_markdown(self):
        """Test markdown validation (basic pass)."""
        doc = Document("# Title", DocumentFormat.MARKDOWN)
        result = self.validator.validate(doc)
        self.assertTrue(result.is_valid)

@pytest.mark.unit
class TestValidateDocumentConvenience(unittest.TestCase):
    @patch('codomyrmex.documents.core.document_validator.DocumentValidator.validate')
    def test_validate_document_wrapper(self, mock_validate):
        """Test convenience wrapper."""
        doc = Document("c", DocumentFormat.TEXT)
        validate_document(doc)
        mock_validate.assert_called_once()
