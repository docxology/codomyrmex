# Languages Module — Agent Coordination

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Docs path**: `docs/modules/languages`
- **Source path**: [../../../src/codomyrmex/languages/](../../../src/codomyrmex/languages/)
- **Human overview**: [README.md](README.md)
- **Functional spec**: [SPEC.md](SPEC.md)
- **Repository agents**: [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Coordinate edits to the language runtime abstraction layer. The source package owns adapters and MCP tools for language-specific code operations; this docs folder explains the module-level role and links to source-owned details.

## Key Files

- `README.md` — module overview and source signposts
- `SPEC.md` — functional expectations for this docs module
- `../../../src/codomyrmex/languages/` — source-owned adapters, MCP tools, and subpackage docs

## Operating Contracts

- Keep language-specific behavior in subpackages such as `python/`, `javascript/`, `go/`, or `rust/`; avoid centralizing unrelated behavior in `base.py`.
- Keep MCP tool changes synchronized with [../../../src/codomyrmex/languages/mcp_tools.py](../../../src/codomyrmex/languages/mcp_tools.py) and source-level docs.
- When adding a language adapter, add source docs in the new subpackage and update this module overview if the adapter is part of the supported public surface.

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Readme**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Source AGENTS**: [../../../src/codomyrmex/languages/AGENTS.md](../../../src/codomyrmex/languages/AGENTS.md)
