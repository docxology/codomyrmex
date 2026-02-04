# Personal AI Infrastructure - Defense Context

**Module**: defense
**Status**: Active

## Context

Fiduciary defense capabilities with active countermeasures against cognitive exploits, including exploit detection, context poisoning, and rabbit hole containment.

## AI Strategy

As an AI agent, when working with this module:

1. **Respect Interfaces**: Use the public API defined in `__init__.py`.
2. **Maintain State**: Ensure any stateful operations are documented in `SPEC.md`.
3. **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.

## Key Files

- `__init__.py`: Public API export.
- `SPEC.md`: Technical specification.

## Future Considerations

- Modularization: Keep dependencies minimal.
- Telemetry: Ensure operations emit performance metrics.
