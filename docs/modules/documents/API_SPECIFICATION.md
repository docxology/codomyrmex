# Documents Module - API Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

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

### HTML

```python
def read_html(file_path: str | Path, encoding: Optional[str] = None) -> str
def write_html(content: str, file_path: str | Path, encoding: Optional[str] = None) -> None
def strip_html_tags(html_content: str) -> str
```

Read/write HTML files and strip HTML tags to extract plain text.

### XML

```python
def read_xml(file_path: str | Path, encoding: Optional[str] = None) -> str
def write_xml(content: str, file_path: str | Path, encoding: Optional[str] = None) -> None
```

Read/write XML files. `read_xml` validates the content parses as XML.

### CSV

```python
def read_csv(file_path: str | Path, encoding: Optional[str] = None) -> list[dict]
def write_csv(
    data: list[dict],
    file_path: str | Path,
    encoding: Optional[str] = None,
    fieldnames: Optional[list[str]] = None,
) -> None
```

Read CSV as a list of dictionaries (keyed by header names). Write CSV from a list of dictionaries.

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
- `ValueError`: If documents list is empty

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

### format_document

```python
def format_document(document: Document, style: str = "default") -> Document
```

Format a document according to a style.

**Parameters:**
- `document` (Document): Document to format
- `style` (str): Formatting style - "default", "compact", or "pretty"

**Returns:** Formatted `Document`

## Search Functions

### InMemoryIndex

```python
class InMemoryIndex:
    def add(self, document: Document) -> None
    def remove(self, doc_id: str) -> None
    def search(self, terms: list[str]) -> list[str]
    def get_document(self, doc_id: str) -> Optional[Document]
    def save(self, path: Path) -> None
    @classmethod
    def load(cls, path: Path) -> "InMemoryIndex"
    @property
    def document_count(self) -> int
```

In-memory inverted index for document search. Supports add, remove, term-based search (AND semantics), and JSON serialization.

### index_document

```python
def index_document(document: Document, index: Optional[InMemoryIndex] = None) -> InMemoryIndex
```

Index a document for search. Creates a new index if none provided.

### create_index

```python
def create_index() -> InMemoryIndex
```

Create a new empty search index.

### search_documents

```python
def search_documents(query: str, index: InMemoryIndex) -> List[Document]
```

Search documents using a query string. Returns matching Document objects.

### search_index

```python
def search_index(query: str, index: InMemoryIndex) -> List[dict]
```

Search index and return results with TF-based scores. Returns list of dicts with `document_id`, `score`, and `document` keys, sorted by score descending.

### QueryBuilder

```python
class QueryBuilder:
    def add_term(self, term: str) -> "QueryBuilder"
    def add_filter(self, field: str, value: str) -> "QueryBuilder"
    def set_sort(self, field: str) -> "QueryBuilder"
    def build(self) -> str
    def to_dict(self) -> dict
```

Fluent builder for constructing search queries.

### build_query

```python
def build_query(terms: List[str], filters: dict = None, sort_by: str = None) -> str
```

Convenience function for building a query string from terms.

## Metadata Functions

### extract_metadata

```python
def extract_metadata(file_path: str | Path) -> dict
```

Extract metadata from a document file (file system metadata + format-specific).

### update_metadata

```python
def update_metadata(file_path: str | Path, metadata: dict) -> None
```

Update metadata for a document file (supports markdown frontmatter).

### get_document_version / set_document_version

```python
def get_document_version(file_path: str | Path) -> Optional[str]
def set_document_version(file_path: str | Path, version: str) -> None
```

## Data Models

### Document

```python
@dataclass
class Document:
    content: Any              # str, dict, list, bytes depending on format
    format: DocumentFormat
    file_path: Optional[Any] = None
    encoding: Optional[str] = None
    metadata: Any = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    document_type: Optional[DocumentType] = None  # auto-derived from format
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = field(default_factory=datetime.now)

    @property
    def type(self) -> DocumentType          # shorthand for document_type
    def get_content_as_string(self) -> str  # serialize content to string
    def to_dict(self) -> dict               # serialize document to dict
```

### DocumentFormat

```python
class DocumentFormat(Enum):
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    PDF = "pdf"
    RTF = "rtf"
    DOCX = "docx"
    XLSX = "xlsx"
    PY = "py"
    JS = "js"
```

### DocumentType

```python
class DocumentType(Enum):
    TEXT = "text"
    MARKUP = "markup"
    STRUCTURED = "structured"
    BINARY = "binary"
    CODE = "code"
```

### DocumentMetadata

```python
@dataclass
class DocumentMetadata:
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    version: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    custom_fields: dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "DocumentMetadata"
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> "DocumentMetadata"
```

### MetadataField

```python
@dataclass
class MetadataField:
    name: str
    value: Any
    data_type: Optional[str] = None
    source: Optional[str] = None
```

### ValidationResult

```python
class ValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
```

Supports truthiness: `if result:` checks `is_valid`.

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

Cache directory defaults to `~/.codomyrmex/documents_cache` or uses `CODOMYRMEX_CACHE_DIR` environment variable.

### get_config / set_config

```python
def get_config() -> DocumentsConfig
def set_config(config: DocumentsConfig) -> None
```

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
