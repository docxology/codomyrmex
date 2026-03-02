# Git Operations Docs -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation subdirectory for the git_operations module. Contains API
specifications, MCP tool definitions, usage examples, and operational
guides. This is NOT a Python module -- no executable code is present.

## Contents

| File | Format | Description |
|------|--------|-------------|
| `API_SPECIFICATION.md` | Markdown | Programmatic API documentation |
| `MCP_TOOL_SPECIFICATION.md` | Markdown | 34 MCP tool definitions for git operations |
| `USAGE_EXAMPLES.md` | Markdown | Practical usage examples and workflows |
| `REPOSITORY_MANAGEMENT_GUIDE.md` | Markdown | Repository management operations guide |
| `METADATA_SYSTEM_GUIDE.md` | Markdown | Repository metadata system guide |
| `CHANGELOG.md` | Markdown | Version history |
| `SECURITY.md` | Markdown | Security considerations |

## Architecture

Flat directory of Markdown documentation files. No Python code, no imports,
no module hierarchy. Documentation is consumed by developers and AI agents
for understanding git_operations capabilities.

## Dependencies

- **Internal**: None (static documentation)
- **External**: None

## Constraints

- Documentation must be kept in sync with actual API surface.
- MCP tool specifications must match `@mcp_tool` decorators in `mcp_tools.py`.
- All files are UTF-8 encoded Markdown.

## Error Handling

- Not applicable (static documentation files).
