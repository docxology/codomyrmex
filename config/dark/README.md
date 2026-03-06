# Dark Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

PDF dark mode utilities providing inversion, brightness, contrast, and sepia filters for PDF documents. Supports preset modes and custom filter chains.

## Configuration Options

The dark module operates with sensible defaults and does not require environment variable configuration. Requires optional dependencies: `uv sync --extra dark`. Filter parameters (inversion level, brightness, contrast) are set per-document.

## PAI Integration

PAI agents interact with dark through direct Python imports. Requires optional dependencies: `uv sync --extra dark`. Filter parameters (inversion level, brightness, contrast) are set per-document.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep dark

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/dark/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
