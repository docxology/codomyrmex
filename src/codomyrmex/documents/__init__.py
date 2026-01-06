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

__version__ = "0.1.0"

# Import core document operations
try:
    from .core.document_reader import DocumentReader, read_document
    from .core.document_writer import DocumentWriter, write_document
    from .core.document_parser import DocumentParser, parse_document
    from .core.document_validator import DocumentValidator, validate_document
    CORE_AVAILABLE = True
except ImportError:
    DocumentReader = None
    DocumentWriter = None
    DocumentParser = None
    DocumentValidator = None
    read_document = None
    write_document = None
    parse_document = None
    validate_document = None
    CORE_AVAILABLE = False

# Import format handlers
try:
    from .formats.markdown_handler import read_markdown, write_markdown
    from .formats.json_handler import read_json, write_json
    from .formats.yaml_handler import read_yaml, write_yaml
    from .formats.text_handler import read_text, write_text
    FORMATS_AVAILABLE = True
except ImportError:
    read_markdown = None
    write_markdown = None
    read_json = None
    write_json = None
    read_yaml = None
    write_yaml = None
    read_text = None
    write_text = None
    FORMATS_AVAILABLE = False

# Import PDF handler (optional)
try:
    from .formats.pdf_handler import read_pdf, write_pdf, PDFDocument
    PDF_AVAILABLE = True
except ImportError:
    read_pdf = None
    write_pdf = None
    PDFDocument = None
    PDF_AVAILABLE = False

# Import transformation capabilities
try:
    from .transformation.converter import convert_document
    from .transformation.merger import merge_documents
    from .transformation.splitter import split_document
    TRANSFORMATION_AVAILABLE = True
except ImportError:
    convert_document = None
    merge_documents = None
    split_document = None
    TRANSFORMATION_AVAILABLE = False

# Import metadata operations
try:
    from .metadata.extractor import extract_metadata
    from .metadata.manager import update_metadata
    from .metadata.versioning import get_document_version
    METADATA_AVAILABLE = True
except ImportError:
    extract_metadata = None
    update_metadata = None
    get_document_version = None
    METADATA_AVAILABLE = False

# Import search capabilities
try:
    from .search.indexer import index_document
    from .search.searcher import search_documents
    SEARCH_AVAILABLE = True
except ImportError:
    index_document = None
    search_documents = None
    SEARCH_AVAILABLE = False

# Import models
try:
    from .models.document import Document, DocumentFormat
    from .models.metadata import DocumentMetadata
    MODELS_AVAILABLE = True
except ImportError:
    Document = None
    DocumentFormat = None
    DocumentMetadata = None
    MODELS_AVAILABLE = False

# Build __all__ dynamically
__all__ = []

if CORE_AVAILABLE:
    __all__.extend([
        "DocumentReader",
        "DocumentWriter",
        "DocumentParser",
        "DocumentValidator",
        "read_document",
        "write_document",
        "parse_document",
        "validate_document",
    ])

if FORMATS_AVAILABLE:
    __all__.extend([
        "read_markdown",
        "write_markdown",
        "read_json",
        "write_json",
        "read_yaml",
        "write_yaml",
        "read_text",
        "write_text",
    ])

if PDF_AVAILABLE:
    __all__.extend([
        "read_pdf",
        "write_pdf",
        "PDFDocument",
    ])

if TRANSFORMATION_AVAILABLE:
    __all__.extend([
        "convert_document",
        "merge_documents",
        "split_document",
    ])

if METADATA_AVAILABLE:
    __all__.extend([
        "extract_metadata",
        "update_metadata",
        "get_document_version",
    ])

if SEARCH_AVAILABLE:
    __all__.extend([
        "index_document",
        "search_documents",
    ])

if MODELS_AVAILABLE:
    __all__.extend([
        "Document",
        "DocumentFormat",
        "DocumentMetadata",
    ])


