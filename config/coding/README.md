# Coding Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unified module for code execution, sandboxing, review, monitoring, and debugging. Provides a comprehensive toolkit for running, analyzing, and fixing code programmatically.

## Configuration Options

The coding module operates with sensible defaults and does not require environment variable configuration. Code execution runs in sandboxed environments with configurable resource limits (CPU, memory, timeout). Review uses static analysis rules.

## MCP Tools

This module exposes 5 MCP tool(s):

- `code_execute`
- `code_list_languages`
- `code_review_file`
- `code_review_project`
- `code_debug`

## PAI Integration

PAI agents invoke coding tools through the MCP bridge. Code execution runs in sandboxed environments with configurable resource limits (CPU, memory, timeout). Review uses static analysis rules.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep coding

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/coding/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
