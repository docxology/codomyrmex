# Personal AI Infrastructure - Core Context

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

**Module**: core
**Status**: Active

## Context

Core git operations for commit, push, pull, clone, and repository state management.

## AI Strategy

As an AI agent, when working with this module:

1. **Respect Interfaces**: Use the public API defined in `__init__.py`.
2. **Maintain State**: Ensure any stateful operations are documented in `SPEC.md`.
3. **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.
4. **State Isolation**: Pass `metadata_file` for task-scoped work. Tests and
   ephemeral agents should use a temporary path; never write under the
   installed package or source checkout.

## Key Files

- `__init__.py`: Public API export.
- `SPEC.md`: Technical specification.
- `metadata.py`: Runtime state selection and persistence.

## Future Considerations

- Modularization: Keep dependencies minimal.
- Telemetry: Ensure operations emit performance metrics.
