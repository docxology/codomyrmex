"""
Documents Module for Codomyrmex.

The Documents module provides robust, abstractable methods for reading and writing
various document formats. It functions like a "printer's shop and library or post office"
- handling the mechanics of document I/O operations, distinct from the documentation
module which focuses on the semantics of technical documentation.

This module supports:
- Multiple document formats (markdown, JSON, PDF, YAML, XML, CSV, HTML, text)
- Document operations (read, write, parse, validate, convert, merge, split)
- Metadata extraction and management
- Document search and indexing
- Document templates and formatting
- Document versioning

Integration:
- Uses `logging_monitoring` for all logging
- Relies on `environment_setup` for environment validation
"""

import contextlib

__version__ = "0.1.0"

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

# Import core document operations
try:
    from .core.document_parser import DocumentParser, parse_document
    from .core.document_reader import DocumentReader, read_document
    from .core.document_validator import (
        DocumentValidator,
        ValidationResult,
        validate_document,
    )
    from .core.document_writer import DocumentWriter, write_document

    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

# Import format handlers
try:
    from .formats.json_handler import read_json, write_json
    from .formats.markdown_handler import read_markdown, write_markdown
    from .formats.text_handler import read_text, write_text
    from .formats.yaml_handler import read_yaml, write_yaml

    FORMATS_AVAILABLE = True
except ImportError:
    FORMATS_AVAILABLE = False

# Import PDF handler (optional)
try:
    from .formats.pdf_handler import PDFDocument, read_pdf, write_pdf

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Import new format handlers
try:
    from .formats.html_handler import read_html, write_html

    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

try:
    from .formats.xml_handler import read_xml, write_xml

    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

try:
    from .formats.csv_handler import read_csv, write_csv

    CSV_AVAILABLE = True
except ImportError:
    CSV_AVAILABLE = False

# Import transformation capabilities
try:
    from .transformation.converter import convert_document
    from .transformation.formatter import format_document
    from .transformation.merger import merge_documents
    from .transformation.splitter import split_document

    TRANSFORMATION_AVAILABLE = True
except ImportError:
    TRANSFORMATION_AVAILABLE = False

# Import metadata operations
try:
    from .metadata.extractor import extract_metadata
    from .metadata.manager import update_metadata
    from .metadata.versioning import get_document_version

    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False

# Import search capabilities
try:
    from .search.indexer import InMemoryIndex, create_index, index_document
    from .search.query_builder import QueryBuilder, build_query
    from .search.searcher import search_documents, search_index

    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

# Import models
try:
    from .models.document import Document, DocumentFormat, DocumentType
    from .models.metadata import DocumentMetadata, MetadataField

    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

# Import config
try:
    from .config import DocumentsConfig, get_config, set_config

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


def cli_commands():
    """Return CLI commands for the documents module."""

    def _list_formats():
        """list document formats."""
        print("Documents Module - Supported Formats:")
        formats = [
            ("markdown", FORMATS_AVAILABLE),
            ("json", FORMATS_AVAILABLE),
            ("yaml", FORMATS_AVAILABLE),
            ("text", FORMATS_AVAILABLE),
            ("pdf", PDF_AVAILABLE),
            ("html", HTML_AVAILABLE),
            ("xml", XML_AVAILABLE),
            ("csv", CSV_AVAILABLE),
        ]
        for name, available in formats:
            status = "available" if available else "unavailable"
            print(f"  {name:12s} - {status}")

    def _convert_document():
        """Convert document (shows conversion capabilities)."""
        print("Documents Module - Conversion:")
        if TRANSFORMATION_AVAILABLE:
            print("  convert_document: available")
            print("  merge_documents:  available")
            print("  split_document:   available")
            print("  format_document:  available")
        else:
            print("  Transformation capabilities unavailable")
            print("  Install document transformation dependencies")

    return {
        "formats": _list_formats,
        "convert": _convert_document,
    }


# Build __all__ dynamically
__all__ = ["cli_commands"]

if CORE_AVAILABLE:
    __all__.extend(
        [
            "DocumentParser",
            "DocumentReader",
            "DocumentValidator",
            "DocumentWriter",
            "ValidationResult",
            "parse_document",
            "read_document",
            "validate_document",
            "write_document",
        ]
    )

if FORMATS_AVAILABLE:
    __all__.extend(
        [
            "read_json",
            "read_markdown",
            "read_text",
            "read_yaml",
            "write_json",
            "write_markdown",
            "write_text",
            "write_yaml",
        ]
    )

if PDF_AVAILABLE:
    __all__.extend(
        [
            "PDFDocument",
            "read_pdf",
            "write_pdf",
        ]
    )

if HTML_AVAILABLE:
    __all__.extend(
        [
            "read_html",
            "write_html",
        ]
    )

if XML_AVAILABLE:
    __all__.extend(
        [
            "read_xml",
            "write_xml",
        ]
    )

if CSV_AVAILABLE:
    __all__.extend(
        [
            "read_csv",
            "write_csv",
        ]
    )

if TRANSFORMATION_AVAILABLE:
    __all__.extend(
        [
            "convert_document",
            "format_document",
            "merge_documents",
            "split_document",
        ]
    )

if METADATA_AVAILABLE:
    __all__.extend(
        [
            "extract_metadata",
            "get_document_version",
            "update_metadata",
        ]
    )

if SEARCH_AVAILABLE:
    __all__.extend(
        [
            "InMemoryIndex",
            "QueryBuilder",
            "build_query",
            "create_index",
            "index_document",
            "search_documents",
            "search_index",
        ]
    )

if MODELS_AVAILABLE:
    __all__.extend(
        [
            "Document",
            "DocumentFormat",
            "DocumentMetadata",
            "DocumentType",
            "MetadataField",
        ]
    )

if CONFIG_AVAILABLE:
    __all__.extend(
        [
            "DocumentsConfig",
            "get_config",
            "set_config",
        ]
    )
