# documents/formats

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Format-specific document handlers. Provides conditional read/write support for eight document formats with graceful degradation when optional dependencies are unavailable. Each handler pair is imported conditionally with a corresponding availability flag.

## Key Exports

All exports are conditional based on handler availability:

### Markdown (if available)
- **`read_markdown()`** -- Read and parse Markdown documents
- **`write_markdown()`** -- Write Markdown documents

### JSON (if available)
- **`read_json()`** -- Read and parse JSON documents
- **`write_json()`** -- Write JSON documents

### YAML (if available)
- **`read_yaml()`** -- Read and parse YAML documents
- **`write_yaml()`** -- Write YAML documents

### Text (if available)
- **`read_text()`** -- Read plain text documents
- **`write_text()`** -- Write plain text documents

### PDF (if available)
- **`read_pdf()`** -- Read and parse PDF documents
- **`write_pdf()`** -- Write PDF documents
- **`PDFDocument`** -- PDF document model class

### HTML (if available)
- **`read_html()`** -- Read and parse HTML documents
- **`write_html()`** -- Write HTML documents
- **`strip_html_tags()`** -- Strip HTML tags from content

### XML (if available)
- **`read_xml()`** -- Read and parse XML documents
- **`write_xml()`** -- Write XML documents

### CSV (if available)
- **`read_csv()`** -- Read and parse CSV documents
- **`write_csv()`** -- Write CSV documents

### Availability Flags

Each format has a boolean availability flag: `MARKDOWN_AVAILABLE`, `JSON_AVAILABLE`, `YAML_AVAILABLE`, `TEXT_AVAILABLE`, `PDF_AVAILABLE`, `HTML_AVAILABLE`, `XML_AVAILABLE`, `CSV_AVAILABLE`.

## Directory Contents

- `__init__.py` - Conditional imports and dynamic `__all__` construction (94 lines)
- `markdown_handler.py` - Markdown read/write handler
- `json_handler.py` - JSON read/write handler
- `yaml_handler.py` - YAML read/write handler
- `text_handler.py` - Plain text read/write handler
- `pdf_handler.py` - PDF read/write handler with PDFDocument class
- `html_handler.py` - HTML read/write handler with tag stripping
- `xml_handler.py` - XML read/write handler
- `csv_handler.py` - CSV read/write handler
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [documents](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
