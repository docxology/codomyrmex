# FPF Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Fetch-Parse-Format pipeline for extracting, parsing, and exporting content from URLs. Supports multiple output formats and content transformation.

## Configuration Options

The fpf module operates with sensible defaults and does not require environment variable configuration. URL fetching uses configurable timeout and retry settings. Output format (JSON, Markdown, plain text) is selected per-operation.

## PAI Integration

PAI agents interact with fpf through direct Python imports. URL fetching uses configurable timeout and retry settings. Output format (JSON, Markdown, plain text) is selected per-operation.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep fpf

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/fpf/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
