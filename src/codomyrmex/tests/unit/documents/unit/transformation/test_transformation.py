"""Zero-mock tests for document transformation (convert, merge, split)."""

import pytest

from codomyrmex.documents.models.document import Document, DocumentFormat
from codomyrmex.documents.transformation.converter import convert_document
from codomyrmex.documents.transformation.merger import merge_documents
from codomyrmex.documents.transformation.splitter import split_document


@pytest.mark.unit
class TestTransformation:
    def test_convert_json_to_yaml(self):
        doc = Document({"a": 1}, DocumentFormat.JSON)
        conv = convert_document(doc, DocumentFormat.YAML)
        assert conv.format == DocumentFormat.YAML
        assert conv.content == {"a": 1}

    def test_merge_text_documents(self):
        doc1 = Document("Hello", DocumentFormat.TEXT)
        doc2 = Document("World", DocumentFormat.TEXT)
        merged = merge_documents([doc1, doc2])
        assert merged.format == DocumentFormat.TEXT
        assert "Hello" in merged.content
        assert "World" in merged.content

    def test_split_by_sections(self):
        content = "# Section 1\nContent 1\n# Section 2\nContent 2"
        doc = Document(content, DocumentFormat.MARKDOWN)
        chunks = split_document(doc, {"method": "by_sections"})
        assert len(chunks) == 2
        assert "# Section 1" in chunks[0].content
        assert "# Section 2" in chunks[1].content
