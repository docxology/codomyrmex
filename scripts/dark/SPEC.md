# Dark Mode Processing Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Orchestrator script for the dark module demonstrating PDF dark mode processing with presets and custom filter configurations using PyMuPDF (fitz).

## Functional Requirements

- **dark_orchestrator.py**: Processes PDFs with dark mode filters, supporting multiple presets and custom color configurations


## Execution

**Prerequisites:**
```bash
uv sync --extra dark (requires PyMuPDF/fitz)
```

**Run:**
```bash
uv run python scripts/dark/dark_orchestrator.py
```

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
