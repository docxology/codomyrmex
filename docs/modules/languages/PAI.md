# Languages Module — PAI Notes

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: April 2026

## Public Interface Role

`codomyrmex.languages` gives agents a stable boundary for language-aware code operations. PAI-facing workflows should depend on the module's public adapters and MCP tools, not on private per-language helper functions.

## Integration Guidance

- Use [../../../src/codomyrmex/languages/mcp_tools.py](../../../src/codomyrmex/languages/mcp_tools.py) for agent/tool invocation surfaces.
- Use per-language subpackages for implementation details.
- Keep runtime assumptions explicit: interpreter availability, toolchain paths, and optional dependencies should be validated before execution.

## Navigation

- **Overview**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Source PAI**: [../../../src/codomyrmex/languages/PAI.md](../../../src/codomyrmex/languages/PAI.md)
