# Codomyrmex Agents -- src/codomyrmex/git_operations/docs

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Documentation subdirectory for the git_operations module. This is NOT a Python
module -- it contains no `.py` implementation files. It holds API specifications,
usage examples, security guidelines, and operational guides for the
git_operations system.

## Contents

| File | Role |
|------|------|
| `API_SPECIFICATION.md` | Programmatic API documentation for git_operations |
| `MCP_TOOL_SPECIFICATION.md` | Model Context Protocol tool definitions (34 git_* tools) |
| `USAGE_EXAMPLES.md` | Practical usage examples and workflows |
| `REPOSITORY_MANAGEMENT_GUIDE.md` | Guide for repository management operations |
| `METADATA_SYSTEM_GUIDE.md` | Guide for the repository metadata system |
| `CHANGELOG.md` | Version history and change log |
| `README.md` | Overview documentation |
| `SECURITY.md` | Security considerations and guidelines |

## Operating Contracts

- Documentation files must stay synchronized with the actual git_operations API.
- MCP tool specification must match the `@mcp_tool` decorators in `mcp_tools.py`.
- No Python imports originate from this directory.

## Integration Points

- **Depends on**: Nothing (static documentation)
- **Used by**: Developers, AI agents, and PAI system for understanding git_operations capabilities

## Navigation

- **Parent**: [git_operations](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
