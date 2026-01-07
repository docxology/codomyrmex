# fpf

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Functional interface for working with the First Principles Framework specification. Transforms the static FPF markdown specification into a machine-readable, queryable, and exportable format for use in prompt/context engineering and other applications. Provides fetching, parsing, extraction, indexing, search, export, and visualization capabilities.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `FPF-Spec.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `analyzer.py` – File
- `context_builder.py` – File
- `exporter.py` – File
- `extractor.py` – File
- `fetcher.py` – File
- `graph_generator.py` – File
- `indexer.py` – File
- `models.py` – File
- `parser.py` – File
- `report_generator.py` – File
- `requirements.txt` – File
- `section_exporter.py` – File
- `section_importer.py` – File
- `section_manager.py` – File
- `term_analyzer.py` – File
- `tests/` – Subdirectory
- `visualizer.py` – File
- `visualizer_png.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.fpf import FPFClient, FPFParser, FPFExporter

# Use high-level client
client = FPFClient()
spec = client.load_from_file("FPF-Spec.md")

# Search for patterns
patterns = client.search("testing", filters={"status": "active"})
print(f"Found {len(patterns)} patterns")

# Get specific pattern
pattern = client.get_pattern("T001")
print(f"Pattern: {pattern.name}")

# Build context for prompt engineering
context = client.build_context(pattern_id="T001")
print(f"Context length: {len(context)}")

# Export to JSON
client.export_json("fpf_spec.json")

# Or use lower-level components
parser = FPFParser()
spec = parser.parse_spec(content)
exporter = FPFExporter()
exporter.export_json(spec, output_path)
```

