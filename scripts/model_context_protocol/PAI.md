# Personal AI Infrastructure - Model Context Protocol Context

**Module**: model_context_protocol
**Status**: Active

## Context
This module provides Model Context Protocol capabilities to the Codomyrmex ecosystem.

## AI Strategy
As an AI agent, when working with this module:
1.  **Respect Interfaces**: Use the public API defined in `__init__.py`.
2.  **Maintain State**: Ensure any stateful operations are documented in `SPEC.md`.
3.  **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.

## Key Files
- `__init__.py`: Public API export.
- `SPEC.md`: Technical specification.

## PAI System Bridge

For full documentation on how the MCP server bridges PAI (`~/.claude/skills/PAI/`) and codomyrmex, see [`src/codomyrmex/model_context_protocol/PAI.md`](../../src/codomyrmex/model_context_protocol/PAI.md). The authoritative PAI bridge document is [`/PAI.md`](../../PAI.md).

## Future Considerations
- Modularization: Keep dependencies minimal.
- Telemetry: Ensure operations emit performance metrics.
