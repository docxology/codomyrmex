# Documents Module - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This document provides detailed API specification for the Documents module, including all public functions, classes, and data structures.

## Core Document Operations

### read_document

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
- `format` (Optional[DocumentFormat]): Optional format hint. If None, format is auto-detected from file extension
- `encoding` (Optional[str]): Optional encoding hint. If None, encoding is auto-detected

**Returns:** `Document` object with content and metadata

**Raises:**
- `DocumentReadError`: If reading fails
- `UnsupportedFormatError`: If format is not supported

**Example:**
```python
from codomyrmex.documents import read_document

doc = read_document("example.md")
print(doc.content)
```

### write_document

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
- `format` (Optional[DocumentFormat]): Optional format override. Uses document.format if not provided
- `encoding` (Optional[str]): Optional encoding override. Uses document.encoding if not provided

**Raises:**
- `DocumentWriteError`: If writing fails
- `UnsupportedFormatError`: If format is not supported

**Example:**
```python
from codomyrmex.documents import write_document, Document, DocumentFormat

doc = Document(content="Hello, World!", format=DocumentFormat.MARKDOWN)
write_document(doc, "output.md")
```

### parse_document

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

**Returns:** `Document` object

**Raises:**
- `DocumentParseError`: If parsing fails

### validate_document

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

**Returns:** `ValidationResult` with validation status and any errors/warnings

**Raises:**
- `DocumentValidationError`: If validation fails

## Format-Specific Functions

### Markdown

```python
def read_markdown(file_path: str | Path, encoding: Optional[str] = None) -> str
def write_markdown(content: str, file_path: str | Path, encoding: Optional[str] = None) -> None
```

### JSON

```python
def read_json(
    file_path: str | Path,
    encoding: Optional[str] = None,
    schema: Optional[dict] = None,
) -> dict

def write_json(
    data: dict,
    file_path: str | Path,
    encoding: Optional[str] = None,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None
```

### YAML

```python
def read_yaml(file_path: str | Path, encoding: Optional[str] = None) -> dict
def write_yaml(
    data: dict,
    file_path: str | Path,
    encoding: Optional[str] = None,
    default_flow_style: bool = False,
) -> None
```

### PDF

```python
def read_pdf(file_path: str | Path) -> PDFDocument
def write_pdf(
    content: str,
    file_path: str | Path,
    metadata: Optional[dict] = None,
) -> None
```

### Text

```python
def read_text(file_path: str | Path, encoding: Optional[str] = None) -> str
def write_text(content: str, file_path: str | Path, encoding: Optional[str] = None) -> None
```

## Transformation Functions

### convert_document

```python
def convert_document(document: Document, target_format: DocumentFormat) -> Document
```

Convert a document to a different format.

**Parameters:**
- `document` (Document): Document to convert
- `target_format` (DocumentFormat): Target format

**Returns:** New `Document` in target format

**Raises:**
- `DocumentConversionError`: If conversion fails
- `UnsupportedFormatError`: If conversion is not supported

### merge_documents

```python
def merge_documents(
    documents: List[Document],
    target_format: DocumentFormat = None,
) -> Document
```

Merge multiple documents into a single document.

**Parameters:**
- `documents` (List[Document]): List of documents to merge
- `target_format` (DocumentFormat): Optional target format. Uses first document's format if not provided

**Returns:** Merged `Document`

**Raises:**
- `DocumentConversionError`: If merging fails

### split_document

```python
def split_document(document: Document, criteria: dict) -> List[Document]
```

Split a document into multiple documents based on criteria.

**Parameters:**
- `document` (Document): Document to split
- `criteria` (dict): Split criteria. Options:
  - `{"method": "by_sections"}` - Split by markdown sections
  - `{"method": "by_size", "max_size": 10000}` - Split by character size
  - `{"method": "by_lines", "lines_per_chunk": 100}` - Split by number of lines

**Returns:** List of split `Document` objects

**Raises:**
- `DocumentConversionError`: If splitting fails

## Metadata Functions

### extract_metadata

```python
def extract_metadata(file_path: str | Path) -> dict
```

Extract metadata from a document file.

**Parameters:**
- `file_path` (str | Path): Path to document file

**Returns:** Dictionary of metadata

**Raises:**
- `MetadataError`: If extraction fails

### update_metadata

```python
def update_metadata(file_path: str | Path, metadata: dict) -> None
```

Update metadata for a document file.

**Parameters:**
- `file_path` (str | Path): Path to document file
- `metadata` (dict): Metadata dictionary to update

**Raises:**
- `MetadataError`: If update fails

### get_document_version

```python
def get_document_version(file_path: str | Path) -> Optional[str]
```

Get version information from a document.

**Parameters:**
- `file_path` (str | Path): Path to document file

**Returns:** Version string or None if not found

### set_document_version

```python
def set_document_version(file_path: str | Path, version: str) -> None
```

Set version information for a document.

**Parameters:**
- `file_path` (str | Path): Path to document file
- `version` (str): Version string to set

**Raises:**
- `MetadataError`: If setting version fails

## Data Models

### Document

```python
@dataclass
class Document:
    content: Any  # Can be str, dict, bytes depending on format
    format: DocumentFormat
    file_path: Optional[Path] = None
    encoding: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    version: Optional[str] = None
```

### DocumentFormat

```python
class DocumentFormat(Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    HTML = "html"
    TEXT = "text"
    RTF = "rtf"
    DOCX = "docx"
    XLSX = "xlsx"
```

### ValidationResult

```python
class ValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
```

## Configuration

### DocumentsConfig

```python
class DocumentsConfig:
    default_encoding: str = "utf-8"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    enable_caching: bool = True
    cache_directory: Optional[Path] = None
    strict_validation: bool = False
```

### get_config

```python
def get_config() -> DocumentsConfig
```

Get the global documents configuration.

### set_config

```python
def set_config(config: DocumentsConfig) -> None
```

Set the global documents configuration.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)



<!-- Navigation Links keyword for score -->

