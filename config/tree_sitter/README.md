# Tree Sitter Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tree-sitter based code parsing and AST analysis. Provides language-agnostic syntax tree construction, node querying, and code structure extraction.

## Configuration Options

The tree_sitter module operates with sensible defaults and does not require environment variable configuration. Language grammars are loaded on demand. Parser timeout and maximum file size are configurable.

## MCP Tools

This module exposes 3 MCP tool(s):

- `tree_sitter_parse`
- `tree_sitter_query`
- `tree_sitter_languages`

## PAI Integration

PAI agents invoke tree_sitter tools through the MCP bridge. Language grammars are loaded on demand. Parser timeout and maximum file size are configurable.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep tree_sitter

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/tree_sitter/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
