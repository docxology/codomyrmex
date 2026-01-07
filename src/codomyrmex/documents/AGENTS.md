# Codomyrmex Agents — src/codomyrmex/documents

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
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

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Robust, abstractable methods for reading and writing various document formats. Handles the mechanics of document I/O operations with support for multiple formats (markdown, JSON, PDF, YAML, XML, CSV, HTML, text), document operations (read, write, parse, validate, convert, merge, split), metadata extraction, document search and indexing, and document versioning.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `README.md` – Project file
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `config.py` – Configuration management
- `core/` – Directory containing core document operations (reader, writer, parser, validator)
- `docs/` – Directory containing docs components
- `exceptions.py` – Document-specific exceptions
- `formats/` – Directory containing format handlers (markdown, json, yaml, pdf, text, etc.)
- `metadata/` – Directory containing metadata operations (extractor, manager, versioning)
- `models/` – Directory containing document models (Document, DocumentFormat, DocumentMetadata)
- `requirements.txt` – Project file
- `search/` – Directory containing search and indexing components
- `templates/` – Directory containing document templates
- `tests/` – Directory containing tests components
- `transformation/` – Directory containing transformation components (converter, merger, splitter)
- `utils/` – Directory containing utility components (encoding detection, MIME type detection)

## Key Classes and Functions

### DocumentReader (`core/document_reader.py`)
- `DocumentReader()` – Unified document reader supporting multiple formats
- `read(file_path: str | Path, format: Optional[DocumentFormat] = None, encoding: Optional[str] = None) -> Document` – Read a document from a file with automatic format and encoding detection

### DocumentWriter (`core/document_writer.py`)
- `DocumentWriter()` – Unified document writer supporting multiple formats
- `write(document: Document, file_path: str | Path, format: Optional[DocumentFormat] = None, encoding: Optional[str] = None) -> None` – Write a document to a file

### DocumentParser (`core/document_parser.py`)
- `DocumentParser()` – Format-specific parsing
- `parse(document: Document) -> Any` – Parse document content based on format

### DocumentValidator (`core/document_validator.py`)
- `DocumentValidator()` – Validation and schema checking
- `validate(document: Document, schema: Optional[dict] = None) -> ValidationResult` – Validate document against schema or format rules

### Document (`models/document.py`)
- `Document` (dataclass) – Document model:
  - `content: Any` – Document content (str, dict, bytes depending on format)
  - `format: DocumentFormat` – Document format
  - `file_path: Optional[Path]` – Source file path
  - `encoding: Optional[str]` – Text encoding
  - `metadata: Optional[dict]` – Document metadata
  - `created_at: Optional[datetime]` – Creation timestamp
  - `modified_at: Optional[datetime]` – Modification timestamp
  - `version: Optional[str]` – Document version
- `get_content_as_string() -> str` – Get content as string, converting if necessary

### DocumentFormat (`models/document.py`)
- `DocumentFormat` (Enum) – Supported formats: MARKDOWN, HTML, XML, JSON, YAML, CSV, PDF, DOCX, XLSX, RTF, TEXT

### Module Functions (`__init__.py`)
- `read_document(file_path: str | Path, format: Optional[DocumentFormat] = None, encoding: Optional[str] = None) -> Document` – Read a document from a file
- `write_document(document: Document, file_path: str | Path, format: Optional[DocumentFormat] = None, encoding: Optional[str] = None) -> None` – Write a document to a file
- `parse_document(document: Document) -> Any` – Parse document content
- `validate_document(document: Document, schema: Optional[dict] = None) -> ValidationResult` – Validate document
- `convert_document(document: Document, target_format: DocumentFormat) -> Document` – Convert document between formats
- `merge_documents(documents: List[Document]) -> Document` – Merge multiple documents
- `split_document(document: Document, criteria: dict) -> List[Document]` – Split document based on criteria
- `extract_metadata(document: Document) -> DocumentMetadata` – Extract document metadata
- `search_documents(query: str, corpus: List[Document]) -> List[Document]` – Search documents

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation