# Terminal Interface Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Rich terminal output and formatting for CLI applications. Foundation layer providing colored output, progress bars, tables, and interactive prompts.

## Configuration Options

The terminal_interface module operates with sensible defaults and does not require environment variable configuration. Terminal capabilities (color support, Unicode, width) are auto-detected from TERM and COLORTERM environment variables. Shell path is detected from SHELL.

## MCP Tools

This module exposes 2 MCP tool(s):

- `terminal_execute`
- `terminal_get_info`

## PAI Integration

PAI agents invoke terminal_interface tools through the MCP bridge. Terminal capabilities (color support, Unicode, width) are auto-detected from TERM and COLORTERM environment variables. Shell path is detected from SHELL.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep terminal_interface

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/terminal_interface/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
