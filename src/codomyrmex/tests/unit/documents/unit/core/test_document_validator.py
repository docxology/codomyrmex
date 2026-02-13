"""Zero-Mock tests for DocumentValidator — uses real validation logic."""

import pytest

from codomyrmex.documents.core.document_validator import (
    DocumentValidator,
    validate_document,
)
from codomyrmex.documents.models.document import Document, DocumentFormat


@pytest.mark.unit
class TestDocumentValidator:
    def setup_method(self):
        self.validator = DocumentValidator()

    def test_validate_structured_json(self):
        """Test validation of structured document against schema."""
        doc = Document({"age": 30}, DocumentFormat.JSON)
        schema = {
            "type": "object",
            "properties": {"age": {"type": "integer"}},
        }
        result = self.validator.validate(doc, schema=schema)
        assert result.is_valid

    def test_validate_structured_json_fail(self):
        """Test validation failure."""
        doc = Document({"age": "thirty"}, DocumentFormat.JSON)
        schema = {
            "type": "object",
            "properties": {"age": {"type": "integer"}},
        }
        result = self.validator.validate(doc, schema=schema)
        assert not result.is_valid

    def test_validate_markdown(self):
        """Test markdown validation (basic pass)."""
        doc = Document("# Title", DocumentFormat.MARKDOWN)
        result = self.validator.validate(doc)
        assert result.is_valid


@pytest.mark.unit
class TestValidateDocumentConvenience:
    def test_validate_document_wrapper(self):
        """Test convenience wrapper calls real validation."""
        doc = Document("content", DocumentFormat.TEXT)
        result = validate_document(doc)
        assert result is not None
