# Personal AI Infrastructure - Codex Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: June 2026

**Module**: codex
**Status**: Active

## Context

OpenAI Codex agent integration for code completion, generation, natural
language to code translation, and read-only Codomyrmex access discovery.

## AI Strategy

As an AI agent, when working with this module:

1. **Respect Interfaces**: Use the public API defined in `__init__.py`.
2. **Maintain State**: Ensure any stateful operations are documented in `SPEC.md`.
3. **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.
4. **Inspect Before Dispatch**: Use `get_codex_access_status()` and
   `get_codex_dispatch_catalog()` before launching side-effectful agent work.

## Key Files

- `__init__.py`: Public API export.
- `access.py`: Read-only access status and dispatch catalog.
- `mcp_tools.py`: Codex MCP tools.
- `SPEC.md`: Technical specification.

## Future Considerations

- Modularization: Keep dependencies minimal.
- Telemetry: Ensure operations emit performace metrics.
