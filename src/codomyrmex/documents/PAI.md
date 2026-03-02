# Personal AI Infrastructure — Documents Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Documents module is Codomyrmex's universal document I/O engine — the "printer's shop and library." It reads, writes, parses, validates, converts, merges, and splits documents across multiple formats (Markdown, JSON, PDF, YAML, XML, CSV, HTML, plain text). It handles the **mechanics** of document operations, distinct from the `documentation` module which handles the **semantics** of technical documentation.

## PAI Capabilities

### Multi-Format Document Processing

```python
from codomyrmex.documents import cli_commands

# The module exposes CLI commands for document operations
commands = cli_commands()
# Available: read, write, convert, validate, merge, split
```

### Format Support

| Format | Read | Write | Parse | Validate |
|--------|------|-------|-------|----------|
| Markdown | ✓ | ✓ | ✓ | ✓ |
| JSON | ✓ | ✓ | ✓ | ✓ |
| YAML | ✓ | ✓ | ✓ | ✓ |
| PDF | ✓ | — | ✓ | — |
| XML | ✓ | ✓ | ✓ | ✓ |
| CSV | ✓ | ✓ | ✓ | ✓ |
| HTML | ✓ | ✓ | ✓ | — |
| Plain Text | ✓ | ✓ | — | — |

### Document Operations

| Operation | Description |
|-----------|-------------|
| **Read** | Load document content with metadata extraction |
| **Write** | Write content with format-specific serialization |
| **Parse** | Extract structured data from documents |
| **Validate** | Verify document structure and schema compliance |
| **Convert** | Transform between formats (e.g., Markdown → HTML) |
| **Merge** | Combine multiple documents into one |
| **Split** | Break large documents into sections |

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `cli_commands` | Function | Returns CLI command handlers for document operations |

## PAI Algorithm Phase Mapping

| Phase | Documents Contribution |
|-------|------------------------|
| **OBSERVE** | Read and parse project documents for understanding; extract metadata from source files |
| **THINK** | Provide structured document content for reasoning context |
| **BUILD** | Write generated documentation, reports, and artifacts |
| **EXECUTE** | Convert and merge documents as part of workflows |
| **VERIFY** | Validate document structure, check format compliance |
| **LEARN** | Capture and index documents for knowledge retrieval |

## Architecture Role

**Core Layer** — Foundational document I/O used by `documentation`, `agentic_memory`, `search`, and agent modules. No upward dependencies.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.documents import ...`
- CLI: `codomyrmex documents <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
