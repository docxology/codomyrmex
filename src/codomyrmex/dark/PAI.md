# Personal AI Infrastructure — Dark Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Dark module provides PDF dark mode utilities — converting and rendering PDF documents with dark mode color schemes for improved readability in low-light environments.

## PAI Capabilities

```python
from codomyrmex.dark import PDF_AVAILABLE, pdf, cli_commands

# Check if PDF processing is available
if PDF_AVAILABLE:
    # Process PDFs with dark mode transformations
    result = pdf.convert(input_path="document.pdf", dark_mode=True)

# CLI interface
commands = cli_commands()
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `pdf` | Module | PDF processing and dark mode conversion |
| `PDF_AVAILABLE` | Constant | Whether PDF dependencies are installed |
| `cli_commands` | Function | CLI commands for dark mode operations |

## PAI Algorithm Phase Mapping

| Phase | Dark Contribution |
|-------|-------------------|
| **EXECUTE** | Convert documents to dark mode for processing and display |

## Architecture Role

**Extended Layer** — Utility module for document rendering. Consumed by `documents/` for PDF output formatting.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.dark import ...`
- CLI: `codomyrmex dark <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
