# Personal AI Infrastructure - Jules Context

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

**Module**: jules
**Status**: Active

## Context

Google Jules coding agent integration for async collaborative programming and automated development. Includes powerful swarm orchestration features (`JulesSwarmDispatcher`) for parallel execution of hundreds of background agents.

## AI Strategy

As an AI agent, when working with this module:

1. **Respect Interfaces**: Use the public API defined in `__init__.py` or the high-level `JulesSwarmDispatcher` for batch processing.
2. **Leverage Swarm Pattern**: When firing many distinct tasks, prefer parallel batching via `dispatcher.dispatch(parallel=N)` to distribute LLM load across multiple Jules CLI processes.
3. **Native Merging**: Do not attempt to manually merge Jules code diffs; the CLI natively branches and PRs them asynchronously.
4. **Error Handling**: Wrap external calls in try/except blocks and log using `logging_monitoring`.

## Key Files

- `__init__.py`: Public API export.
- `SPEC.md`: Technical specification.

## Future Considerations

- Modularization: Keep dependencies minimal.
- Telemetry: Ensure operations emit performace metrics.
