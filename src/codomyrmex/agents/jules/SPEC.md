# jules - Functional Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `jules` submodule provides integration with Jules CLI tool. It includes a client wrapper for executing jules commands and integration adapters for Codomyrmex modules.

## Design Principles

### Functionality

- **CLI Integration**: Wraps jules CLI command execution
- **Error Handling**: Handles command failures and timeouts gracefully
- **Integration**: Provides adapters for Codomyrmex modules

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent SPEC**: [../SPEC.md](../SPEC.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

### Architecture Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages chunked batching (`batch_size`) to dispatch agents.
3. **Error Resilience**: Robust exception handling and exponential backoff retry mechanisms wrap `_execute_impl`.
4. **Delegated Source Control**: Branching and merging functionality is natively deferred to the Jules CLI.

### Swarm Batching Architecture

To support massive parallel execution (hundreds of targeted agents), the `JulesSwarmDispatcher` utilizes a compound prompt injection model. Instead of launching 500 individual `julius` shell processes (which risks process exhaustion or rate limits), the dispatcher groups tasks into predefined segments:

- `tasks` list is spliced by `batch_size`.
- A compound prompt combining all tasks in that batch is rendered dynamically.
- The `julius new --parallel N` command natively interprets this batch and handles downstream concurrency.

### "Merging Back In" Subsystem

Codomyrmex does not manually manage `git merge` or patch applications for Jules output. The design explicitly delegates this to the backend:

1. `JulesClient` initiates a `julius new` or equivalent task command.
2. Jules generates a background workspace, determines changes, and (depending on project config) issues a Pull Request.
3. The merge action is asynchronous, finalized by human review or external CI loop.
