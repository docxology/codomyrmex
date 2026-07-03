# Demos MCP Tool Specification

**Version**: v1.3.0 | **Status**: Not MCP-exposed | **Last Updated**: June 2026

## Current MCP Surface

`codomyrmex.demos` does not currently expose production MCP tools. The module
provides a Python registry and a terminal demo runner used by CLI and shell
surfaces.

## Python Surfaces

| Surface | Purpose |
|:---|:---|
| `DemoRegistry` | Register, list, discover, and run demos |
| `demo(...)` | Decorator for registering demo functions |
| `get_registry()` | Return the process-local demo registry |
| `run_terminal_demo(module_name)` | Run known terminal demos for interactive shell integration |

## Future Tool Criteria

If this module gains MCP tools, they should expose read-only listing first and
keep side-effectful demo execution explicit, bounded, and documented here.

## Navigation

- **Python API**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
