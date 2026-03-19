# Personal AI Infrastructure - Fabric Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

**Module**: fabric
**Status**: Active

## Context

Fabric prompt pattern implementation for modular AI workflows with pre-defined interaction templates. Specifically wraps the `danielmiessler/fabric` binary.

## AI Strategy

As an AI agent, when working with this module:

1. **Respect Interfaces**: Use the public API defined in `__init__.py`.
2. **Handle Graceful Degradation**: Always check `is_available()` on orchestrators or managers. Subprocesses will safely simulate failure rather than crash if `fabric` is completely missing.
3. **Maintain State**: Ensure any stateful operations are documented in `SPEC.md`.
4. **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.

## Key Files

- `__init__.py`: Public API export.
- `SPEC.md`: Technical specification.
- `AGENTS.md`: Navigational bounds and zero-mock policy reference.

## Future Considerations

- Modularization: Keep dependencies minimal.
- Telemetry: Operations already parse subprocess timings. Emit metrics smoothly.
