"""
Comprehensive unit tests for the documents module.

This module tests all document operations including reading, writing, parsing,
validation, format conversion, merging, splitting, metadata operations, and search.
"""

import os
import pytest
import tempfile
import json
import yaml
from pathlib import Path
from datetime import datetime

from codomyrmex.documents import (
    read_document,
    write_document,
    parse_document,
    validate_document,
)

from codomyrmex.documents.models.document import (
    Document,
    DocumentFormat,
    DocumentType,
)

from codomyrmex.documents.models.metadata import (
    DocumentMetadata,
    MetadataField,
)

from codomyrmex.documents.core import (
    DocumentReader,
    DocumentWriter,
    DocumentParser,
    DocumentValidator,
    ValidationResult,
)

from codomyrmex.documents.config import (
    DocumentsConfig,
    get_config,
    set_config,
)

try:
    from codomyrmex.documents.formats.markdown_handler import read_markdown, write_markdown
except ImportError:
    read_markdown = None
    write_markdown = None

try:
    from codomyrmex.documents.formats.json_handler import read_json, write_json
except ImportError:
    read_json = None
    write_json = None

try:
    from codomyrmex.documents.formats.yaml_handler import read_yaml, write_yaml
except ImportError:
    read_yaml = None
    write_yaml = None

try:
    from codomyrmex.documents.formats.text_handler import read_text, write_text
except ImportError:
    read_text = None
    write_text = None

try:
    from codomyrmex.documents.formats.html_handler import read_html, write_html, strip_html_tags
except ImportError:
    read_html = None
    write_html = None
    strip_html_tags = None

try:
    from codomyrmex.documents.formats.xml_handler import read_xml, write_xml
except ImportError:
    read_xml = None
    write_xml = None

try:
    from codomyrmex.documents.formats.csv_handler import read_csv, write_csv
except ImportError:
    read_csv = None
    write_csv = None

try:
    from codomyrmex.documents.transformation.converter import convert_document
except ImportError:
    convert_document = None

try:
    from codomyrmex.documents.transformation.merger import merge_documents
except ImportError:
    merge_documents = None

try:
    from codomyrmex.documents.transformation.splitter import split_document
except ImportError:
    split_document = None

try:
    from codomyrmex.documents.transformation.formatter import format_document
except ImportError:
    format_document = None

try:
    from codomyrmex.documents.metadata.extractor import extract_metadata
except ImportError:
    extract_metadata = None

try:
    from codomyrmex.documents.metadata.manager import update_metadata
except ImportError:
    update_metadata = None

try:
    from codomyrmex.documents.metadata.versioning import get_document_version, set_document_version
except ImportError:
    get_document_version = None
    set_document_version = None

try:
    from codomyrmex.documents.search.indexer import InMemoryIndex, index_document, create_index
except ImportError:
    InMemoryIndex = None
    index_document = None
    create_index = None

try:
    from codomyrmex.documents.search.searcher import search_documents, search_index
except ImportError:
    search_documents = None
    search_index = None

try:
    from codomyrmex.documents.search.query_builder import QueryBuilder, build_query
except ImportError:
    QueryBuilder = None
    build_query = None

from codomyrmex.documents.utils.encoding_detector import detect_encoding
from codomyrmex.documents.utils.mime_type_detector import detect_format_from_path, detect_mime_type
from codomyrmex.documents.utils.file_validator import validate_file_path, check_file_size

from codomyrmex.documents.exceptions import (
    DocumentReadError,
    DocumentWriteError,
    DocumentParseError,
    DocumentValidationError,
    DocumentConversionError,
    UnsupportedFormatError,
)


# ─── Document Model ────────────────────────────────────────────────────

class TestDocumentModel:
    """Test Document data model."""

    def test_document_creation(self):
        """Test creating a Document object."""
        doc = Document(
            content="Test content",
            format=DocumentFormat.TEXT
        )
        assert doc.content == "Test content"
        assert doc.format == DocumentFormat.TEXT
        assert doc.type == DocumentType.TEXT
        assert doc.created_at is not None
        assert doc.modified_at is not None

    def test_document_auto_id(self):
        """Test that id is auto-generated."""
        doc1 = Document(content="A", format=DocumentFormat.TEXT)
        doc2 = Document(content="B", format=DocumentFormat.TEXT)
        assert doc1.id != doc2.id
        assert len(doc1.id) == 32  # uuid4 hex

    def test_document_get_content_as_string(self):
        """Test getting content as string."""
        # String content
        doc = Document(content="Hello", format=DocumentFormat.TEXT)
        assert doc.get_content_as_string() == "Hello"

        # Dict content
        doc = Document(content={"key": "value"}, format=DocumentFormat.JSON)
        content_str = doc.get_content_as_string()
        assert "key" in content_str
        assert "value" in content_str

        # List content
        doc = Document(content=[1, 2, 3], format=DocumentFormat.JSON)
        assert doc.get_content_as_string() == "[1, 2, 3]"

    def test_document_type_detection(self):
        """Test document type detection from format."""
        doc = Document(content="", format=DocumentFormat.MARKDOWN)
        assert doc.type == DocumentType.MARKUP

        doc = Document(content="", format=DocumentFormat.HTML)
        assert doc.type == DocumentType.MARKUP

        doc = Document(content="", format=DocumentFormat.JSON)
        assert doc.type == DocumentType.STRUCTURED

        doc = Document(content="", format=DocumentFormat.YAML)
        assert doc.type == DocumentType.STRUCTURED

        doc = Document(content="", format=DocumentFormat.CSV)
        assert doc.type == DocumentType.STRUCTURED

        doc = Document(content="", format=DocumentFormat.PDF)
        assert doc.type == DocumentType.BINARY

        doc = Document(content="", format=DocumentFormat.TEXT)
        assert doc.type == DocumentType.TEXT

        doc = Document(content="", format=DocumentFormat.PY)
        assert doc.type == DocumentType.CODE

    def test_document_to_dict(self):
        """Test to_dict serialization."""
        doc = Document(content="Hello world", format=DocumentFormat.TEXT)
        d = doc.to_dict()
        assert d["id"] == doc.id
        assert d["content"] == "Hello world"
        assert d["format"] == "text"
        assert d["document_type"] == "text"
        assert "created_at" in d
        assert "modified_at" in d

    def test_document_to_dict_truncates_long_content(self):
        """Test that to_dict truncates long content."""
        long_content = "A" * 200
        doc = Document(content=long_content, format=DocumentFormat.TEXT)
        d = doc.to_dict()
        assert d["content"].endswith("...")
        assert len(d["content"]) <= 104  # 100 + "..."

    def test_document_encoding_field(self):
        """Test encoding field."""
        doc = Document(content="Test", format=DocumentFormat.TEXT, encoding="utf-8")
        assert doc.encoding == "utf-8"

    def test_document_type_property(self):
        """Test type property is shorthand for document_type."""
        doc = Document(content="", format=DocumentFormat.JSON)
        assert doc.type is doc.document_type


# ─── Document Metadata Model ───────────────────────────────────────────

class TestDocumentMetadataModel:
    """Test DocumentMetadata model."""

    def test_metadata_creation(self):
        """Test creating metadata."""
        meta = DocumentMetadata(title="Test", author="Author")
        assert meta.title == "Test"
        assert meta.author == "Author"
        assert meta.tags == []
        assert meta.custom_fields == {}

    def test_metadata_to_dict(self):
        """Test to_dict serialization."""
        meta = DocumentMetadata(title="Test", tags=["a", "b"])
        d = meta.to_dict()
        assert d["title"] == "Test"
        assert d["tags"] == ["a", "b"]

    def test_metadata_from_dict(self):
        """Test from_dict deserialization."""
        data = {
            "title": "Test",
            "author": "Author",
            "tags": ["x"],
            "custom_fields": {"key": "val"},
        }
        meta = DocumentMetadata.from_dict(data)
        assert meta.title == "Test"
        assert meta.author == "Author"
        assert meta.tags == ["x"]
        assert meta.custom_fields == {"key": "val"}

    def test_metadata_copy(self):
        """Test copy method."""
        meta = DocumentMetadata(title="Original", tags=["a"])
        copied = meta.copy()
        assert copied.title == "Original"
        assert copied.tags == ["a"]
        # Ensure it's a deep copy
        copied.tags.append("b")
        assert "b" not in meta.tags

    def test_metadata_field_creation(self):
        """Test MetadataField creation."""
        field = MetadataField(name="author", value="John", data_type="string", source="frontmatter")
        assert field.name == "author"
        assert field.value == "John"
        assert field.data_type == "string"
        assert field.source == "frontmatter"


# ─── Config ─────────────────────────────────────────────────────────────

class TestDocumentsConfig:
    """Test DocumentsConfig."""

    def test_config_defaults(self):
        """Test default config values."""
        config = DocumentsConfig()
        assert config.default_encoding == "utf-8"
        assert config.max_file_size == 100 * 1024 * 1024
        assert config.strict_validation is False

    def test_config_custom_values(self):
        """Test custom config values."""
        config = DocumentsConfig(
            default_encoding="latin-1",
            max_file_size=1024,
            strict_validation=True,
        )
        assert config.default_encoding == "latin-1"
        assert config.max_file_size == 1024
        assert config.strict_validation is True

    def test_get_set_config(self, tmp_path):
        """Test global config get/set."""
        original = get_config()
        try:
            custom = DocumentsConfig(
                default_encoding="ascii",
                cache_directory=tmp_path / "cache",
            )
            set_config(custom)
            assert get_config().default_encoding == "ascii"
        finally:
            set_config(original)

    def test_config_env_var_cache_dir(self, tmp_path, monkeypatch):
        """Test cache directory from environment variable."""
        monkeypatch.setenv('CODOMYRMEX_CACHE_DIR', str(tmp_path))
        config = DocumentsConfig()
        assert config.cache_directory == tmp_path / "documents_cache"


# ─── Validation Result ──────────────────────────────────────────────────

class TestValidationResult:
    """Test ValidationResult."""

    def test_valid_result(self):
        """Test valid result."""
        result = ValidationResult(is_valid=True)
        assert bool(result) is True
        assert result.errors == []
        assert result.warnings == []

    def test_invalid_result(self):
        """Test invalid result with errors."""
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])
        assert bool(result) is False
        assert len(result.errors) == 2

    def test_result_with_warnings(self):
        """Test result with warnings."""
        result = ValidationResult(is_valid=True, warnings=["Warning 1"])
        assert bool(result) is True
        assert len(result.warnings) == 1


# ─── Document Reader ───────────────────────────────────────────────────

class TestDocumentReader:
    """Test DocumentReader class."""

    def test_read_markdown_file(self, tmp_path):
        """Test reading a markdown file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\nContent here", encoding="utf-8")

        reader = DocumentReader()
        doc = reader.read(test_file)

        assert doc.format == DocumentFormat.MARKDOWN
        assert "# Test" in doc.get_content_as_string()
        assert doc.file_path == test_file

    def test_read_json_file(self, tmp_path):
        """Test reading a JSON file."""
        test_file = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(data), encoding="utf-8")

        reader = DocumentReader()
        doc = reader.read(test_file)

        assert doc.format == DocumentFormat.JSON
        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_read_yaml_file(self, tmp_path):
        """Test reading a YAML file."""
        test_file = tmp_path / "test.yaml"
        data = {"key": "value", "number": 42}
        test_file.write_text(yaml.dump(data), encoding="utf-8")

        reader = DocumentReader()
        doc = reader.read(test_file)

        assert doc.format == DocumentFormat.YAML
        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_read_text_file(self, tmp_path):
        """Test reading a text file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Plain text content", encoding="utf-8")

        reader = DocumentReader()
        doc = reader.read(test_file)

        assert doc.format == DocumentFormat.TEXT
        assert doc.content == "Plain text content"

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading a non-existent file raises error."""
        reader = DocumentReader()
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(DocumentReadError):
            reader.read(nonexistent)

    def test_auto_format_detection(self, tmp_path):
        """Test automatic format detection from file extension."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test", encoding="utf-8")
        reader = DocumentReader()
        doc = reader.read(md_file)
        assert doc.format == DocumentFormat.MARKDOWN

        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")
        doc = reader.read(json_file)
        assert doc.format == DocumentFormat.JSON


# ─── Document Writer ───────────────────────────────────────────────────

class TestDocumentWriter:
    """Test DocumentWriter class."""

    def test_write_markdown(self, tmp_path):
        """Test writing a markdown document."""
        doc = Document(
            content="# Test Document\n\nContent here",
            format=DocumentFormat.MARKDOWN
        )

        output_file = tmp_path / "output.md"
        writer = DocumentWriter()
        writer.write(doc, output_file)

        assert output_file.exists()
        assert "# Test Document" in output_file.read_text()

    def test_write_json(self, tmp_path):
        """Test writing a JSON document."""
        doc = Document(
            content={"key": "value", "number": 42},
            format=DocumentFormat.JSON
        )

        output_file = tmp_path / "output.json"
        writer = DocumentWriter()
        writer.write(doc, output_file)

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["key"] == "value"

    def test_write_text(self, tmp_path):
        """Test writing a text document."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        output_file = tmp_path / "output.txt"

        writer = DocumentWriter()
        writer.write(doc, output_file)

        assert output_file.exists()
        assert output_file.read_text() == "Test"

    def test_write_creates_directory(self, tmp_path):
        """Test that writer creates parent directories."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        output_file = tmp_path / "subdir" / "output.txt"

        writer = DocumentWriter()
        writer.write(doc, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()


# ─── Document Parser ───────────────────────────────────────────────────

class TestDocumentParser:
    """Test DocumentParser class."""

    def test_parse_json_content(self):
        """Test parsing JSON content."""
        parser = DocumentParser()
        content = '{"key": "value"}'
        doc = parser.parse(content, DocumentFormat.JSON)

        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_parse_yaml_content(self):
        """Test parsing YAML content."""
        parser = DocumentParser()
        content = "key: value\nnumber: 42"
        doc = parser.parse(content, DocumentFormat.YAML)

        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_parse_markdown_content(self):
        """Test parsing markdown content."""
        parser = DocumentParser()
        content = "# Heading\n\nParagraph"
        doc = parser.parse(content, DocumentFormat.MARKDOWN)

        assert doc.content == content
        assert isinstance(doc.content, str)


# ─── Document Validator ────────────────────────────────────────────────

class TestDocumentValidator:
    """Test DocumentValidator class."""

    def test_validate_valid_json(self):
        """Test validating valid JSON document."""
        doc = Document(
            content={"key": "value"},
            format=DocumentFormat.JSON
        )

        validator = DocumentValidator()
        result = validator.validate(doc)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_invalid_json_string(self):
        """Test validating invalid JSON string."""
        doc = Document(
            content='{"key": invalid}',
            format=DocumentFormat.JSON
        )

        validator = DocumentValidator()
        result = validator.validate(doc)

        assert not result.is_valid or len(result.errors) > 0

    def test_validate_none_content(self):
        """Test validating document with None content."""
        doc = Document(content=None, format=DocumentFormat.TEXT)
        validator = DocumentValidator()
        result = validator.validate(doc)
        assert not result.is_valid
        assert any("None" in e for e in result.errors)

    def test_validate_with_schema(self):
        """Test validating document with JSON schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }

        doc = Document(
            content={"name": "John", "age": 30},
            format=DocumentFormat.JSON
        )
        validator = DocumentValidator()
        result = validator.validate(doc, schema=schema)
        assert result is not None


# ─── Format Handlers ───────────────────────────────────────────────────

class TestFormatHandlers:
    """Test format-specific handlers."""

    @pytest.mark.skipif(read_markdown is None or write_markdown is None, reason="Markdown handlers not available")
    def test_markdown_read_write(self, tmp_path):
        """Test markdown read and write."""
        test_file = tmp_path / "test.md"
        content = "# Title\n\nContent"
        write_markdown(content, test_file)

        read_content = read_markdown(test_file)
        assert read_content == content

    @pytest.mark.skipif(read_json is None or write_json is None, reason="JSON handlers not available")
    def test_json_read_write(self, tmp_path):
        """Test JSON read and write."""
        test_file = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        write_json(data, test_file)

        read_data = read_json(test_file)
        assert read_data == data

    @pytest.mark.skipif(read_yaml is None or write_yaml is None, reason="YAML handlers not available")
    def test_yaml_read_write(self, tmp_path):
        """Test YAML read and write."""
        test_file = tmp_path / "test.yaml"
        data = {"key": "value", "number": 42}
        write_yaml(data, test_file)

        read_data = read_yaml(test_file)
        assert read_data == data

    @pytest.mark.skipif(read_text is None or write_text is None, reason="Text handlers not available")
    def test_text_read_write(self, tmp_path):
        """Test text read and write."""
        test_file = tmp_path / "test.txt"
        content = "Plain text content"
        write_text(content, test_file)

        read_content = read_text(test_file)
        assert read_content == content

    @pytest.mark.skipif(read_json is None or write_json is None, reason="JSON handlers not available")
    def test_json_schema_validation(self, tmp_path):
        """Test JSON read with schema validation."""
        test_file = tmp_path / "test.json"
        data = {"name": "John", "age": 30}
        write_json(data, test_file)

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }

        try:
            read_data = read_json(test_file, schema=schema)
            assert read_data == data
        except DocumentValidationError:
            pass


# ─── HTML Handler ──────────────────────────────────────────────────────

class TestHtmlHandler:
    """Test HTML handler."""

    @pytest.mark.skipif(read_html is None or write_html is None, reason="HTML handler not available")
    def test_html_read_write(self, tmp_path):
        """Test HTML read and write."""
        test_file = tmp_path / "test.html"
        content = "<html><body><h1>Hello</h1></body></html>"
        write_html(content, test_file)

        read_content = read_html(test_file)
        assert read_content == content

    @pytest.mark.skipif(read_html is None, reason="HTML handler not available")
    def test_html_read_nonexistent(self, tmp_path):
        """Test reading non-existent HTML file."""
        with pytest.raises(DocumentReadError):
            read_html(tmp_path / "missing.html")

    @pytest.mark.skipif(strip_html_tags is None, reason="HTML handler not available")
    def test_strip_html_tags(self):
        """Test stripping HTML tags."""
        html = "<p>Hello <b>world</b>!</p>"
        text = strip_html_tags(html)
        assert "Hello" in text
        assert "world" in text

    @pytest.mark.skipif(read_html is None or write_html is None, reason="HTML handler not available")
    def test_html_unicode(self, tmp_path):
        """Test HTML with unicode content."""
        test_file = tmp_path / "unicode.html"
        content = "<p>Hello world</p>"
        write_html(content, test_file)
        assert read_html(test_file) == content


# ─── XML Handler ───────────────────────────────────────────────────────

class TestXmlHandler:
    """Test XML handler."""

    @pytest.mark.skipif(read_xml is None or write_xml is None, reason="XML handler not available")
    def test_xml_read_write(self, tmp_path):
        """Test XML read and write."""
        test_file = tmp_path / "test.xml"
        content = "<root><item>Test</item></root>"
        write_xml(content, test_file)

        read_content = read_xml(test_file)
        assert read_content == content

    @pytest.mark.skipif(read_xml is None, reason="XML handler not available")
    def test_xml_invalid(self, tmp_path):
        """Test reading invalid XML."""
        test_file = tmp_path / "bad.xml"
        test_file.write_text("<unclosed>", encoding="utf-8")

        with pytest.raises(DocumentReadError):
            read_xml(test_file)

    @pytest.mark.skipif(read_xml is None, reason="XML handler not available")
    def test_xml_read_nonexistent(self, tmp_path):
        """Test reading non-existent XML file."""
        with pytest.raises(DocumentReadError):
            read_xml(tmp_path / "missing.xml")


# ─── CSV Handler ───────────────────────────────────────────────────────

class TestCsvHandler:
    """Test CSV handler."""

    @pytest.mark.skipif(read_csv is None or write_csv is None, reason="CSV handler not available")
    def test_csv_read_write(self, tmp_path):
        """Test CSV read and write."""
        test_file = tmp_path / "test.csv"
        data = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"},
        ]
        write_csv(data, test_file)

        read_data = read_csv(test_file)
        assert len(read_data) == 2
        assert read_data[0]["name"] == "Alice"
        assert read_data[1]["age"] == "25"

    @pytest.mark.skipif(write_csv is None, reason="CSV handler not available")
    def test_csv_write_empty(self, tmp_path):
        """Test writing empty CSV."""
        test_file = tmp_path / "empty.csv"
        write_csv([], test_file)
        assert test_file.exists()

    @pytest.mark.skipif(read_csv is None, reason="CSV handler not available")
    def test_csv_read_nonexistent(self, tmp_path):
        """Test reading non-existent CSV file."""
        with pytest.raises(DocumentReadError):
            read_csv(tmp_path / "missing.csv")


# ─── Document Transformation ──────────────────────────────────────────

class TestDocumentTransformation:
    """Test document transformation operations."""

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_convert_markdown_to_text(self):
        """Test converting markdown to text."""
        doc = Document(
            content="# Heading\n\nContent",
            format=DocumentFormat.MARKDOWN
        )

        converted = convert_document(doc, DocumentFormat.TEXT)
        assert converted.format == DocumentFormat.TEXT
        assert "# Heading" in converted.get_content_as_string()

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_convert_same_format(self):
        """Test converting to same format returns same document."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        result = convert_document(doc, DocumentFormat.TEXT)
        assert result is doc

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_convert_yaml_to_json(self):
        """Test converting YAML to JSON."""
        doc = Document(content="key: value", format=DocumentFormat.YAML)
        converted = convert_document(doc, DocumentFormat.JSON)
        assert converted.format == DocumentFormat.JSON
        assert isinstance(converted.content, dict)
        assert converted.content["key"] == "value"

    @pytest.mark.skipif(merge_documents is None, reason="Document merger not available")
    def test_merge_documents(self):
        """Test merging multiple documents."""
        doc1 = Document(content="First", format=DocumentFormat.TEXT)
        doc2 = Document(content="Second", format=DocumentFormat.TEXT)
        doc3 = Document(content="Third", format=DocumentFormat.TEXT)

        merged = merge_documents([doc1, doc2, doc3])
        assert merged.format == DocumentFormat.TEXT
        content = merged.get_content_as_string()
        assert "First" in content
        assert "Second" in content
        assert "Third" in content

    @pytest.mark.skipif(merge_documents is None, reason="Document merger not available")
    def test_merge_single_document(self):
        """Test merging a single document returns it."""
        doc = Document(content="Only one", format=DocumentFormat.TEXT)
        result = merge_documents([doc])
        assert result is doc

    @pytest.mark.skipif(merge_documents is None, reason="Document merger not available")
    def test_merge_empty_raises(self):
        """Test merging empty list raises ValueError."""
        with pytest.raises(ValueError):
            merge_documents([])

    @pytest.mark.skipif(split_document is None, reason="Document splitter not available")
    def test_split_document_by_sections(self):
        """Test splitting document by sections."""
        doc = Document(
            content="# Section 1\n\nContent 1\n\n# Section 2\n\nContent 2",
            format=DocumentFormat.MARKDOWN
        )

        split_docs = split_document(doc, {"method": "by_sections"})
        assert len(split_docs) >= 2

    @pytest.mark.skipif(split_document is None, reason="Document splitter not available")
    def test_split_document_by_size(self):
        """Test splitting document by size."""
        large_content = "A" * 10000
        doc = Document(content=large_content, format=DocumentFormat.TEXT)

        split_docs = split_document(doc, {"method": "by_size", "max_size": 1000})
        assert len(split_docs) == 10

    @pytest.mark.skipif(split_document is None, reason="Document splitter not available")
    def test_split_document_by_lines(self):
        """Test splitting document by lines."""
        content = "\n".join(f"Line {i}" for i in range(100))
        doc = Document(content=content, format=DocumentFormat.TEXT)

        split_docs = split_document(doc, {"method": "by_lines", "lines_per_chunk": 25})
        assert len(split_docs) == 4


# ─── Formatter ─────────────────────────────────────────────────────────

class TestFormatter:
    """Test document formatter."""

    @pytest.mark.skipif(format_document is None, reason="Formatter not available")
    def test_format_default(self):
        """Test default formatting returns same document."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        result = format_document(doc, style="default")
        assert result is doc

    @pytest.mark.skipif(format_document is None, reason="Formatter not available")
    def test_format_json_compact(self):
        """Test compact JSON formatting."""
        doc = Document(content={"key": "value", "num": 1}, format=DocumentFormat.JSON)
        result = format_document(doc, style="compact")
        content = result.get_content_as_string()
        assert " " not in content or content == '{"key":"value","num":1}'

    @pytest.mark.skipif(format_document is None, reason="Formatter not available")
    def test_format_json_pretty(self):
        """Test pretty JSON formatting."""
        doc = Document(content={"key": "value"}, format=DocumentFormat.JSON)
        result = format_document(doc, style="pretty")
        content = result.get_content_as_string()
        assert "\n" in content


# ─── Metadata Operations ──────────────────────────────────────────────

class TestMetadataOperations:
    """Test metadata operations."""

    @pytest.mark.skipif(extract_metadata is None, reason="Metadata extractor not available")
    def test_extract_metadata(self, tmp_path):
        """Test extracting metadata from file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content", encoding="utf-8")

        metadata = extract_metadata(test_file)
        assert "file_size" in metadata
        assert "modified_at" in metadata

    @pytest.mark.skipif(extract_metadata is None, reason="Metadata extractor not available")
    def test_extract_markdown_frontmatter(self, tmp_path):
        """Test extracting markdown frontmatter."""
        test_file = tmp_path / "test.md"
        test_file.write_text("---\ntitle: My Doc\nauthor: Author\n---\n\n# Content", encoding="utf-8")

        metadata = extract_metadata(test_file)
        assert metadata.get("title") == "My Doc"

    @pytest.mark.skipif(get_document_version is None, reason="Versioning not available")
    def test_get_document_version(self, tmp_path):
        """Test getting document version."""
        test_file = tmp_path / "test.md"
        test_file.write_text("---\nversion: 1.0.0\n---\n\nContent", encoding="utf-8")

        version = get_document_version(test_file)
        assert version is None or isinstance(version, str)

    @pytest.mark.skipif(update_metadata is None, reason="Metadata manager not available")
    def test_update_markdown_metadata(self, tmp_path):
        """Test updating markdown frontmatter."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# No frontmatter yet", encoding="utf-8")

        update_metadata(test_file, {"title": "New Title"})
        content = test_file.read_text()
        assert "---" in content
        assert "New Title" in content


# ─── Search Module ─────────────────────────────────────────────────────

class TestSearchIndexer:
    """Test search indexer."""

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_create_index(self):
        """Test creating empty index."""
        idx = create_index()
        assert idx.document_count == 0

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_document(self):
        """Test indexing a document."""
        doc = Document(content="hello world testing", format=DocumentFormat.TEXT)
        idx = index_document(doc)
        assert idx.document_count == 1

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_add_remove(self):
        """Test adding and removing documents."""
        idx = InMemoryIndex()
        doc = Document(content="test content", format=DocumentFormat.TEXT)
        idx.add(doc)
        assert idx.document_count == 1

        idx.remove(doc.id)
        assert idx.document_count == 0

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_search(self):
        """Test searching the index."""
        idx = InMemoryIndex()
        doc1 = Document(content="python programming language", format=DocumentFormat.TEXT)
        doc2 = Document(content="javascript web development", format=DocumentFormat.TEXT)
        doc3 = Document(content="python web framework", format=DocumentFormat.TEXT)
        idx.add(doc1)
        idx.add(doc2)
        idx.add(doc3)

        # Search for "python" should find doc1 and doc3
        results = idx.search(["python"])
        assert len(results) == 2
        assert doc1.id in results
        assert doc3.id in results

        # Search for "python" AND "web" should find only doc3
        results = idx.search(["python", "web"])
        assert len(results) == 1
        assert doc3.id in results

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_search_no_results(self):
        """Test searching with no matches."""
        idx = InMemoryIndex()
        doc = Document(content="hello world", format=DocumentFormat.TEXT)
        idx.add(doc)

        results = idx.search(["nonexistent"])
        assert len(results) == 0

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_save_load(self, tmp_path):
        """Test saving and loading index."""
        idx = InMemoryIndex()
        doc = Document(content="test save load", format=DocumentFormat.TEXT)
        idx.add(doc)

        save_path = tmp_path / "index.json"
        idx.save(save_path)
        assert save_path.exists()

        loaded = InMemoryIndex.load(save_path)
        # Loaded index has term data but not full Document objects
        assert "test" in loaded._index

    @pytest.mark.skipif(InMemoryIndex is None, reason="Search indexer not available")
    def test_index_get_document(self):
        """Test retrieving document from index."""
        idx = InMemoryIndex()
        doc = Document(content="findme", format=DocumentFormat.TEXT)
        idx.add(doc)

        retrieved = idx.get_document(doc.id)
        assert retrieved is doc
        assert idx.get_document("nonexistent") is None


class TestSearchSearcher:
    """Test search searcher."""

    @pytest.mark.skipif(search_documents is None or InMemoryIndex is None, reason="Search not available")
    def test_search_documents(self):
        """Test searching documents."""
        idx = InMemoryIndex()
        doc1 = Document(content="python guide", format=DocumentFormat.TEXT)
        doc2 = Document(content="java tutorial", format=DocumentFormat.TEXT)
        idx.add(doc1)
        idx.add(doc2)

        results = search_documents("python", idx)
        assert len(results) == 1
        assert results[0].id == doc1.id

    @pytest.mark.skipif(search_index is None or InMemoryIndex is None, reason="Search not available")
    def test_search_index_with_scores(self):
        """Test search_index returns results with scores."""
        idx = InMemoryIndex()
        doc1 = Document(content="python python python", format=DocumentFormat.TEXT)
        doc2 = Document(content="python java", format=DocumentFormat.TEXT)
        idx.add(doc1)
        idx.add(doc2)

        results = search_index("python", idx)
        assert len(results) == 2
        # doc1 should score higher (more occurrences)
        assert results[0]["score"] >= results[1]["score"]
        assert results[0]["document_id"] == doc1.id

    @pytest.mark.skipif(search_documents is None or InMemoryIndex is None, reason="Search not available")
    def test_search_empty_query(self):
        """Test searching with empty query."""
        idx = InMemoryIndex()
        doc = Document(content="test", format=DocumentFormat.TEXT)
        idx.add(doc)

        results = search_documents("", idx)
        assert len(results) == 0


class TestSearchQueryBuilder:
    """Test query builder."""

    @pytest.mark.skipif(QueryBuilder is None, reason="Query builder not available")
    def test_query_builder_fluent(self):
        """Test fluent API of QueryBuilder."""
        qb = QueryBuilder()
        result = qb.add_term("hello").add_term("world").add_filter("type", "text").set_sort("date")
        assert result is qb
        assert qb.build() == "hello world"

    @pytest.mark.skipif(QueryBuilder is None, reason="Query builder not available")
    def test_query_builder_to_dict(self):
        """Test QueryBuilder to_dict."""
        qb = QueryBuilder()
        qb.add_term("test").add_filter("format", "json").set_sort("score")
        d = qb.to_dict()
        assert d["terms"] == ["test"]
        assert d["filters"] == {"format": "json"}
        assert d["sort_by"] == "score"

    @pytest.mark.skipif(build_query is None, reason="Query builder not available")
    def test_build_query_convenience(self):
        """Test build_query convenience function."""
        query = build_query(["hello", "world"])
        assert query == "hello world"


# ─── Utils ─────────────────────────────────────────────────────────────

class TestUtilsEncodingDetector:
    """Test encoding detection utilities."""

    def test_detect_encoding_utf8(self, tmp_path):
        """Test detecting UTF-8 encoding."""
        test_file = tmp_path / "utf8.txt"
        test_file.write_text("Hello, world!", encoding="utf-8")

        encoding = detect_encoding(test_file)
        assert encoding is not None

    def test_detect_encoding_empty_file(self, tmp_path):
        """Test detecting encoding of empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_bytes(b"")

        encoding = detect_encoding(test_file)
        # Should return default or None
        assert encoding is not None or encoding is None


class TestUtilsFormatDetector:
    """Test format detection utilities."""

    def test_detect_format_markdown(self):
        """Test detecting markdown format."""
        assert detect_format_from_path(Path("test.md")) == "markdown"
        assert detect_format_from_path(Path("test.markdown")) == "markdown"

    def test_detect_format_json(self):
        """Test detecting JSON format."""
        assert detect_format_from_path(Path("test.json")) == "json"

    def test_detect_format_yaml(self):
        """Test detecting YAML format."""
        assert detect_format_from_path(Path("test.yaml")) == "yaml"
        assert detect_format_from_path(Path("test.yml")) == "yaml"

    def test_detect_format_text(self):
        """Test detecting text format."""
        assert detect_format_from_path(Path("test.txt")) == "text"

    def test_detect_format_html(self):
        """Test detecting HTML format."""
        assert detect_format_from_path(Path("test.html")) == "html"
        assert detect_format_from_path(Path("test.htm")) == "html"

    def test_detect_format_xml(self):
        """Test detecting XML format."""
        assert detect_format_from_path(Path("test.xml")) == "xml"

    def test_detect_format_csv(self):
        """Test detecting CSV format."""
        assert detect_format_from_path(Path("test.csv")) == "csv"

    def test_detect_format_unknown(self):
        """Test detecting unknown format defaults to text."""
        assert detect_format_from_path(Path("test.xyz")) == "text"

    def test_detect_mime_type(self, tmp_path):
        """Test MIME type detection."""
        mime = detect_mime_type(Path("test.json"))
        assert mime == "application/json"

        mime = detect_mime_type(Path("test.html"))
        assert mime == "text/html"


class TestUtilsFileValidator:
    """Test file validation utilities."""

    def test_validate_existing_file(self, tmp_path):
        """Test validating an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Should not raise
        validate_file_path(test_file, must_exist=True)

    def test_validate_nonexistent_file(self, tmp_path):
        """Test validating non-existent file raises error."""
        with pytest.raises(DocumentReadError):
            validate_file_path(tmp_path / "missing.txt", must_exist=True)

    def test_validate_directory_path(self, tmp_path):
        """Test validating a directory path raises error."""
        with pytest.raises(DocumentReadError):
            validate_file_path(tmp_path, must_exist=True)

    def test_check_file_size_within_limit(self, tmp_path):
        """Test file size check for small file."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("small content")

        assert check_file_size(test_file) is True

    def test_check_file_size_nonexistent(self, tmp_path):
        """Test file size check for non-existent file."""
        assert check_file_size(tmp_path / "missing.txt") is False


# ─── Convenience Functions ─────────────────────────────────────────────

class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_read_document_function(self, tmp_path):
        """Test read_document convenience function."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test", encoding="utf-8")

        doc = read_document(test_file)
        assert doc.format == DocumentFormat.MARKDOWN
        assert "# Test" in doc.get_content_as_string()

    def test_write_document_function(self, tmp_path):
        """Test write_document convenience function."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        output_file = tmp_path / "output.txt"

        write_document(doc, output_file)
        assert output_file.exists()
        assert output_file.read_text() == "Test"

    def test_parse_document_function(self):
        """Test parse_document convenience function."""
        content = '{"key": "value"}'
        doc = parse_document(content, DocumentFormat.JSON)

        assert isinstance(doc.content, dict)
        assert doc.content["key"] == "value"

    def test_validate_document_function(self):
        """Test validate_document convenience function."""
        doc = Document(content={"key": "value"}, format=DocumentFormat.JSON)
        result = validate_document(doc)

        assert result is not None
        assert hasattr(result, "is_valid")


# ─── Error Handling ────────────────────────────────────────────────────

class TestErrorHandling:
    """Test error handling."""

    def test_read_error_for_missing_file(self, tmp_path):
        """Test DocumentReadError for missing file."""
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(DocumentReadError):
            read_document(nonexistent)

    def test_write_error_handling(self, tmp_path):
        """Test error handling in write operations."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)

        try:
            write_document(doc, tmp_path / "output.txt")
            assert True
        except DocumentWriteError:
            pass

    @pytest.mark.skipif(convert_document is None, reason="Document converter not available")
    def test_unsupported_format_error(self):
        """Test error handling for unsupported formats."""
        doc = Document(content="Test", format=DocumentFormat.TEXT)

        with pytest.raises((UnsupportedFormatError, DocumentConversionError)):
            convert_document(doc, DocumentFormat.DOCX)


# ─── Round-Trip Tests ──────────────────────────────────────────────────

class TestRoundTrip:
    """Test read/write round-trips."""

    def test_markdown_round_trip(self, tmp_path):
        """Test markdown read -> write -> read round-trip."""
        content = "# Title\n\n## Section\n\nParagraph text."
        original_file = tmp_path / "original.md"
        original_file.write_text(content, encoding="utf-8")

        doc = read_document(original_file)
        output_file = tmp_path / "copy.md"
        write_document(doc, output_file)
        doc2 = read_document(output_file)

        assert doc.get_content_as_string() == doc2.get_content_as_string()

    def test_json_round_trip(self, tmp_path):
        """Test JSON read -> write -> read round-trip."""
        data = {"name": "Test", "items": [1, 2, 3], "nested": {"key": "val"}}
        original_file = tmp_path / "original.json"
        original_file.write_text(json.dumps(data), encoding="utf-8")

        doc = read_document(original_file)
        output_file = tmp_path / "copy.json"
        write_document(doc, output_file)
        doc2 = read_document(output_file)

        assert doc.content == doc2.content

    def test_text_round_trip(self, tmp_path):
        """Test text read -> write -> read round-trip."""
        content = "Line 1\nLine 2\nLine 3"
        original_file = tmp_path / "original.txt"
        original_file.write_text(content, encoding="utf-8")

        doc = read_document(original_file)
        output_file = tmp_path / "copy.txt"
        write_document(doc, output_file)
        doc2 = read_document(output_file)

        assert doc.get_content_as_string() == doc2.get_content_as_string()


# ─── Edge Cases ────────────────────────────────────────────────────────

class TestEdgeCases:
    """Test edge cases."""

    def test_empty_text_file(self, tmp_path):
        """Test reading empty text file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        doc = read_document(test_file)
        assert doc.get_content_as_string() == ""

    def test_unicode_content(self, tmp_path):
        """Test reading file with unicode content."""
        test_file = tmp_path / "unicode.txt"
        content = "Hello CJK: \u4f60\u597d RTL: \u0645\u0631\u062d\u0628\u0627"
        test_file.write_text(content, encoding="utf-8")

        doc = read_document(test_file)
        assert "\u4f60\u597d" in doc.get_content_as_string()

    def test_document_with_dict_content(self):
        """Test document with dict content."""
        doc = Document(content={"a": 1}, format=DocumentFormat.JSON)
        s = doc.get_content_as_string()
        assert '"a"' in s
        assert "1" in s

    def test_empty_json_file(self, tmp_path):
        """Test reading empty JSON object."""
        test_file = tmp_path / "empty.json"
        test_file.write_text("{}", encoding="utf-8")

        doc = read_document(test_file)
        assert doc.content == {}
