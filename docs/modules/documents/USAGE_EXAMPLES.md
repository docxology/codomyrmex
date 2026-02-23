# Documents Module - Usage Examples

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Basic Reading and Writing

### Reading a Markdown File

```python
from codomyrmex.documents import read_document, DocumentFormat

# Auto-detect format
doc = read_document("example.md")
print(doc.content)

# Specify format explicitly
doc = read_document("example.md", format=DocumentFormat.MARKDOWN)
```

### Writing a Document

```python
from codomyrmex.documents import write_document, Document, DocumentFormat

doc = Document(
    content="# Hello, World!

This is a markdown document.",
    format=DocumentFormat.MARKDOWN
)
write_document(doc, "output.md")
```

### Reading JSON with Schema Validation

```python
from codomyrmex.documents import read_json

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    },
    "required": ["name"]
}

data = read_json("data.json", schema=schema)
```

### Writing JSON

```python
from codomyrmex.documents import write_json

data = {
    "name": "John Doe",
    "age": 30,
    "city": "New York"
}

write_json(data, "output.json", indent=2)
```

## Format Conversion

### Convert Markdown to JSON

```python
from codomyrmex.documents import read_document, convert_document, DocumentFormat

# Read markdown
md_doc = read_document("example.md")

# Convert to JSON
json_doc = convert_document(md_doc, DocumentFormat.JSON)

# Write JSON
from codomyrmex.documents import write_document
write_document(json_doc, "example.json")
```

### Convert JSON to YAML

```python
from codomyrmex.documents import read_document, convert_document, DocumentFormat

json_doc = read_document("data.json", format=DocumentFormat.JSON)
yaml_doc = convert_document(json_doc, DocumentFormat.YAML)

write_document(yaml_doc, "data.yaml")
```

## Document Merging

### Merge Multiple Markdown Files

```python
from codomyrmex.documents import read_document, merge_documents, write_document

# Read multiple documents
doc1 = read_document("chapter1.md")
doc2 = read_document("chapter2.md")
doc3 = read_document("chapter3.md")

# Merge them
merged = merge_documents([doc1, doc2, doc3])

# Write merged document
write_document(merged, "complete_book.md")
```

### Merge JSON Documents

```python
from codomyrmex.documents import read_document, merge_documents, DocumentFormat

json1 = read_document("config1.json", format=DocumentFormat.JSON)
json2 = read_document("config2.json", format=DocumentFormat.JSON)

merged_config = merge_documents([json1, json2], target_format=DocumentFormat.JSON)
write_document(merged_config, "merged_config.json")
```

## Document Splitting

### Split by Sections

```python
from codomyrmex.documents import read_document, split_document

doc = read_document("long_document.md")

# Split by markdown sections
sections = split_document(doc, {"method": "by_sections"})

for i, section in enumerate(sections):
    write_document(section, f"section_{i}.md")
```

### Split by Size

```python
from codomyrmex.documents import read_document, split_document

doc = read_document("large_document.txt")

# Split into chunks of 10,000 characters
chunks = split_document(doc, {"method": "by_size", "max_size": 10000})

for i, chunk in enumerate(chunks):
    write_document(chunk, f"chunk_{i}.txt")
```

### Split by Lines

```python
from codomyrmex.documents import read_document, split_document

doc = read_document("data.txt")

# Split into chunks of 100 lines
chunks = split_document(doc, {"method": "by_lines", "lines_per_chunk": 100})

for i, chunk in enumerate(chunks):
    write_document(chunk, f"part_{i}.txt")
```

## Metadata Operations

### Extract Metadata

```python
from codomyrmex.documents import extract_metadata

metadata = extract_metadata("document.pdf")
print(f"Title: {metadata.get('title')}")
print(f"Author: {metadata.get('author')}")
print(f"File size: {metadata.get('file_size')} bytes")
```

### Update Metadata

```python
from codomyrmex.documents import update_metadata

update_metadata(
    "document.md",
    {
        "title": "My Document",
        "author": "John Doe",
        "tags": ["python", "documentation"]
    }
)
```

### Document Versioning

```python
from codomyrmex.documents import get_document_version, set_document_version

# Set version
set_document_version("document.md", "1.0.0")

# Get version
version = get_document_version("document.md")
print(f"Document version: {version}")
```

## PDF Operations

### Read PDF

```python
from codomyrmex.documents import read_pdf

pdf_doc = read_pdf("document.pdf")
print(f"Page count: {pdf_doc.page_count}")
print(f"Content: {pdf_doc.content[:500]}")  # First 500 characters
print(f"Metadata: {pdf_doc.metadata}")
```

### Write PDF

```python
from codomyrmex.documents import write_pdf

content = """
# My Document

This is the content of my PDF document.

It can contain multiple paragraphs and formatting.
"""

write_pdf(
    content,
    "output.pdf",
    metadata={
        "title": "My PDF Document",
        "author": "John Doe",
        "subject": "Example PDF"
    }
)
```

## Document Validation

### Validate Document

```python
from codomyrmex.documents import read_document, validate_document

doc = read_document("data.json", format=DocumentFormat.JSON)

# Validate without schema
result = validate_document(doc)
if result.is_valid:
    print("Document is valid")
else:
    print(f"Validation errors: {result.errors}")
```

### Validate with Schema

```python
from codomyrmex.documents import read_document, validate_document, DocumentFormat

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "number", "minimum": 0}
    },
    "required": ["name", "email"]
}

doc = read_document("user.json", format=DocumentFormat.JSON)
result = validate_document(doc, schema=schema)

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

## Advanced Usage

### Custom Configuration

```python
from codomyrmex.documents import DocumentsConfig, set_config
from pathlib import Path

config = DocumentsConfig(
    default_encoding="utf-8",
    max_file_size=50 * 1024 * 1024,  # 50MB
    enable_caching=True,
    cache_directory=Path.home() / ".my_cache",
    strict_validation=True
)

set_config(config)
```

### Error Handling

```python
from codomyrmex.documents import read_document
from codomyrmex.documents.exceptions import DocumentReadError, UnsupportedFormatError

try:
    doc = read_document("example.xyz")
except UnsupportedFormatError as e:
    print(f"Format not supported: {e.context.get('format')}")
except DocumentReadError as e:
    print(f"Failed to read document: {e}")
    print(f"File path: {e.context.get('file_path')}")
```

### Batch Processing

```python
from pathlib import Path
from codomyrmex.documents import read_document, convert_document, write_document, DocumentFormat

input_dir = Path("markdown_files")
output_dir = Path("json_files")
output_dir.mkdir(exist_ok=True)

for md_file in input_dir.glob("*.md"):
    try:
        # Read markdown
        doc = read_document(md_file)
        
        # Convert to JSON
        json_doc = convert_document(doc, DocumentFormat.JSON)
        
        # Write JSON
        output_file = output_dir / f"{md_file.stem}.json"
        write_document(json_doc, output_file)
        
        print(f"Converted {md_file.name} to {output_file.name}")
    except Exception as e:
        print(f"Error processing {md_file.name}: {e}")
```

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)



<!-- Navigation Links keyword for score -->

