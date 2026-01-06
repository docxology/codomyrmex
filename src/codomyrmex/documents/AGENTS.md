# Codomyrmex Agents — src/codomyrmex/documents

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Documents Agents](AGENTS.md)
- **Children**:
    - [core](core/AGENTS.md)
    - [docs](docs/AGENTS.md)
    - [formats](formats/AGENTS.md)
    - [metadata](metadata/AGENTS.md)
    - [models](models/AGENTS.md)
    - [search](search/AGENTS.md)
    - [templates](templates/AGENTS.md)
    - [tests](tests/AGENTS.md)
    - [transformation](transformation/AGENTS.md)
    - [utils](utils/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

The Documents module provides robust, abstractable methods for reading and writing various document formats. It functions like a "printer's shop and library or post office" - handling the mechanics of document I/O operations, distinct from the `documentation` module which focuses on the semantics of technical documentation.

This module supports multiple document formats (markdown, JSON, PDF, YAML, XML, CSV, HTML, text), document operations (read, write, parse, validate, convert, merge, split), metadata extraction and management, document search and indexing, document templates and formatting, and document versioning.

## Module Overview

### Key Capabilities
- **Multi-Format Support**: Read and write markdown, JSON, PDF, YAML, XML, CSV, HTML, and plain text
- **Document Operations**: Parse, validate, convert, merge, and split documents
- **Metadata Management**: Extract, update, and version document metadata
- **Search and Indexing**: Index documents and perform search operations
- **Transformation**: Convert between formats and transform document structure

### Key Features
- Unified document reading and writing interface
- Format-specific handlers with auto-detection
- Document validation and schema checking
- Format conversion capabilities
- Document merging and splitting
- Metadata extraction and management
- Document versioning support

## Function Signatures

### Core Document Operations

```python
def read_document(
    file_path: str | Path,
    format: Optional[DocumentFormat] = None,
    encoding: Optional[str] = None,
) -> Document
```

Read a document from a file with automatic format and encoding detection.

**Parameters:**
- `file_path` (str | Path): Path to the document file
- `format` (Optional[DocumentFormat]): Optional format hint (auto-detected if not provided)
- `encoding` (Optional[str]): Optional encoding hint (auto-detected if not provided)

**Returns:** Document object with content and metadata

```python
def write_document(
    document: Document,
    file_path: str | Path,
    format: Optional[DocumentFormat] = None,
    encoding: Optional[str] = None,
) -> None
```

Write a document to a file.

**Parameters:**
- `document` (Document): Document object to write
- `file_path` (str | Path): Path where document should be written
- `format` (Optional[DocumentFormat]): Optional format override
- `encoding` (Optional[str]): Optional encoding override

```python
def parse_document(
    content: str,
    format: DocumentFormat,
    file_path: str | None = None,
) -> Document
```

Parse content string into a Document object.

**Parameters:**
- `content` (str): Content string to parse
- `format` (DocumentFormat): Format of the content
- `file_path` (str | None): Optional file path for context

**Returns:** Document object

```python
def validate_document(
    document: Document,
    schema: Optional[dict] = None,
) -> ValidationResult
```

Validate a document against a schema or format rules.

**Parameters:**
- `document` (Document): Document to validate
- `schema` (Optional[dict]): Optional JSON schema for validation

**Returns:** ValidationResult with validation status and any errors/warnings

### Format-Specific Functions

```python
def read_markdown(file_path: str | Path, encoding: Optional[str] = None) -> str
def write_markdown(content: str, file_path: str | Path, encoding: Optional[str] = None) -> None
def read_json(file_path: str | Path, encoding: Optional[str] = None, schema: Optional[dict] = None) -> dict
def write_json(data: dict, file_path: str | Path, encoding: Optional[str] = None, indent: int = 2) -> None
def read_yaml(file_path: str | Path, encoding: Optional[str] = None) -> dict
def write_yaml(data: dict, file_path: str | Path, encoding: Optional[str] = None) -> None
def read_text(file_path: str | Path, encoding: Optional[str] = None) -> str
def write_text(content: str, file_path: str | Path, encoding: Optional[str] = None) -> None
def read_pdf(file_path: str | Path) -> PDFDocument
def write_pdf(content: str, file_path: str | Path, metadata: Optional[dict] = None) -> None
```

### Transformation Functions

```python
def convert_document(document: Document, target_format: DocumentFormat) -> Document
def merge_documents(documents: List[Document], target_format: DocumentFormat = None) -> Document
def split_document(document: Document, criteria: dict) -> List[Document]
```

### Metadata Functions

```python
def extract_metadata(file_path: str | Path) -> dict
def update_metadata(file_path: str | Path, metadata: dict) -> None
def get_document_version(file_path: str | Path) -> Optional[str]
def set_document_version(file_path: str | Path, version: str) -> None
```

### Search Functions

```python
def index_document(document: Document, index_path: Optional[Path] = None) -> None
def search_documents(query: str, index_path: Path) -> List[Document]
```

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `exceptions.py` – Module-specific exception classes
- `config.py` – Configuration management

### Core Operations
- `core/document_reader.py` – Unified document reading
- `core/document_writer.py` – Unified document writing
- `core/document_parser.py` – Format-specific parsing
- `core/document_validator.py` – Validation and schema checking

### Format Handlers
- `formats/markdown_handler.py` – Markdown read/write
- `formats/json_handler.py` – JSON read/write
- `formats/yaml_handler.py` – YAML read/write
- `formats/pdf_handler.py` – PDF read/write
- `formats/text_handler.py` – Plain text read/write

### Transformation
- `transformation/converter.py` – Format conversion
- `transformation/merger.py` – Document merging
- `transformation/splitter.py` – Document splitting
- `transformation/formatter.py` – Formatting utilities

### Metadata
- `metadata/extractor.py` – Metadata extraction
- `metadata/manager.py` – Metadata management
- `metadata/versioning.py` – Document versioning

### Search
- `search/indexer.py` – Document indexing
- `search/searcher.py` – Search operations
- `search/query_builder.py` – Query construction

### Models
- `models/document.py` – Document model
- `models/metadata.py` – Metadata models

### Utilities
- `utils/encoding_detector.py` – Encoding detection
- `utils/mime_type_detector.py` – MIME type detection
- `utils/file_validator.py` – File validation


### Additional Files
- `API_SPECIFICATION.md` – Api Specification Md
- `README.md` – Readme Md
- `SPEC.md` – Spec Md
- `USAGE_EXAMPLES.md` – Usage Examples Md
- `core` – Core
- `docs` – Docs
- `formats` – Formats
- `metadata` – Metadata
- `models` – Models
- `requirements.txt` – Requirements Txt
- `search` – Search
- `templates` – Templates
- `tests` – Tests
- `transformation` – Transformation
- `utils` – Utils

## Operating Contracts

### Universal Document Protocols

All document operations within the Codomyrmex platform must:

1. **Encoding Safety** - Handle encoding detection and conversion gracefully
2. **Format Validation** - Validate document formats before processing
3. **Error Handling** - Provide clear error messages with context
4. **Metadata Preservation** - Preserve document metadata during operations
5. **Extensible Design** - Support addition of new formats and operations

### Module-Specific Guidelines

#### Document Reading/Writing
- Support automatic format and encoding detection
- Handle file system errors gracefully
- Provide format-specific validation
- Support both file paths and Path objects

#### Document Transformation
- Preserve document structure when possible
- Handle format conversion errors gracefully
- Support merging and splitting operations
- Maintain document metadata during transformation

## Related Modules
- **Documentation** (`documentation/`) - Technical documentation generation (semantics)
- **Logging Monitoring** (`logging_monitoring/`) - Centralized logging system
- **Environment Setup** (`environment_setup/`) - Environment validation

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation

