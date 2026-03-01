"""Unit tests for document data models -- Document, DocumentMetadata, config, and validation results."""

import os

import pytest

from codomyrmex.documents.config import (
    DocumentsConfig,
    get_config,
    set_config,
)
from codomyrmex.documents.core import (
    ValidationResult,
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


# --- Document Model --------------------------------------------------------

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


# --- Document Metadata Model -----------------------------------------------

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


# --- Config -----------------------------------------------------------------

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

    def test_config_env_var_cache_dir(self, tmp_path):
        """Test cache directory from environment variable."""
        original = os.environ.get('CODOMYRMEX_CACHE_DIR')
        os.environ['CODOMYRMEX_CACHE_DIR'] = str(tmp_path)
        try:
            config = DocumentsConfig()
            assert config.cache_directory == tmp_path / "documents_cache"
        finally:
            if original is None:
                os.environ.pop('CODOMYRMEX_CACHE_DIR', None)
            else:
                os.environ['CODOMYRMEX_CACHE_DIR'] = original


# --- Validation Result ------------------------------------------------------

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
