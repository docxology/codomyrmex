# Languages Module Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: April 2026

## Purpose

The `codomyrmex.languages` module standardizes language-specific code workflows behind a common package boundary. It supports adapters for multiple programming languages and exposes MCP tools where language-aware operations need to be invoked by agents or orchestration layers.

## Source of Truth

- Source implementation: [../../../src/codomyrmex/languages/](../../../src/codomyrmex/languages/)
- Source specification: [../../../src/codomyrmex/languages/SPEC.md](../../../src/codomyrmex/languages/SPEC.md)
- MCP tools: [../../../src/codomyrmex/languages/mcp_tools.py](../../../src/codomyrmex/languages/mcp_tools.py)

## Design Constraints

1. Preserve a common adapter contract for language runtimes.
2. Keep per-language behavior in subpackages.
3. Route agent-facing operations through MCP tools rather than ad-hoc imports from orchestration code.
4. Keep docs and tests aligned when adding or removing supported languages.

## Navigation

- **Overview**: [README.md](README.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **Parent**: [../README.md](../README.md)
