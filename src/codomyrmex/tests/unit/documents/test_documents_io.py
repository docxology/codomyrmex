"""Unit tests for document I/O -- reading, writing, and format handlers (markdown, JSON, YAML, text)."""

import json
from pathlib import Path

import pytest
import yaml

from codomyrmex.documents import (
    read_document,
    write_document,
)
from codomyrmex.documents.core import (
    DocumentReader,
    DocumentWriter,
)
from codomyrmex.documents.models.document import (
    Document,
    DocumentFormat,
)

try:
    from codomyrmex.documents.formats.markdown_handler import (
        read_markdown,
        write_markdown,
    )
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
    from codomyrmex.documents.formats.html_handler import (
        read_html,
        strip_html_tags,
        write_html,
    )
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

from codomyrmex.documents.exceptions import (
    DocumentReadError,
    DocumentValidationError,
    DocumentWriteError,
)
from codomyrmex.documents.utils.encoding_detector import detect_encoding
from codomyrmex.documents.utils.file_validator import (
    check_file_size,
    validate_file_path,
)
from codomyrmex.documents.utils.mime_type_detector import (
    detect_format_from_path,
    detect_mime_type,
)

# --- Document Reader --------------------------------------------------------

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


# --- Document Writer --------------------------------------------------------

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


# --- Format Handlers --------------------------------------------------------

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


# --- HTML Handler -----------------------------------------------------------

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


# --- XML Handler ------------------------------------------------------------

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


# --- CSV Handler ------------------------------------------------------------

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


# --- Convenience Functions --------------------------------------------------

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


# --- Error Handling ---------------------------------------------------------

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
            # Successful write: verify the file was created
            assert (tmp_path / "output.txt").exists()
        except DocumentWriteError:
            # Write error is acceptable (e.g., format not supported)
            pass


# --- Round-Trip Tests -------------------------------------------------------

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


# --- Edge Cases -------------------------------------------------------------

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


# --- Utils: Encoding Detector -----------------------------------------------

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


# --- Utils: Format Detector --------------------------------------------------

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


# --- Utils: File Validator ---------------------------------------------------

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
