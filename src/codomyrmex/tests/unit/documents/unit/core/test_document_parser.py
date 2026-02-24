"""Zero-Mock tests for DocumentParser — uses real parsing logic."""

import pytest

from codomyrmex.documents.core.document_parser import DocumentParser, parse_document
from codomyrmex.documents.exceptions import DocumentParseError
from codomyrmex.documents.models.document import DocumentFormat


@pytest.mark.unit
class TestDocumentParser:
    """Test suite for DocumentParser."""
    def setup_method(self):
        self.parser = DocumentParser()

    def test_parse_json(self):
        """Test parsing JSON string."""
        content = '{"key": "value"}'
        doc = self.parser.parse(content, DocumentFormat.JSON)
        assert doc.content == {"key": "value"}
        assert doc.format == DocumentFormat.JSON

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        content = "{invalid: json}"
        with pytest.raises(DocumentParseError):
            self.parser.parse(content, DocumentFormat.JSON)

    def test_parse_markdown(self):
        """Test parsing Markdown (returns string content)."""
        content = "# Title"
        doc = self.parser.parse(content, DocumentFormat.MARKDOWN)
        assert doc.content == "# Title"

    def test_parse_text(self):
        """Test parsing plain text."""
        content = "Hello world"
        doc = self.parser.parse(content, DocumentFormat.TEXT)
        assert doc.content == "Hello world"


@pytest.mark.unit
class TestParseDocumentConvenience:
    """Test suite for ParseDocumentConvenience."""
    def test_parse_document_wrapper(self):
        """Test convenience wrapper calls real parser."""
        result = parse_document('{"a": 1}', DocumentFormat.JSON)
        assert result is not None
        assert result.content == {"a": 1}
