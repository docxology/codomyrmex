# Codomyrmex Agents — src/codomyrmex/agents/jules

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Jules agent implementation for asynchronous background task processing and code operations.

## Active Components

- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `jules_client.py` – Client wrapper and swarm dispatcher
- `jules_integration.py` – Workflow adapters

## Jules Agent Methods

The submodule exposes the following key methods to orchestrate agent operations:

### JulesClient

- `execute_jules_command(command, args=None, config_path=None)`: Directly executes a specific Jules subcommand with exponential-backoff retries.
- `dispatch_swarm(tasks, repo, parallel=100, batch_size=10)`: Dispatches a massive swarm array. Automatically groups `tasks` into chunks of `batch_size` and calls `julius new --repo <repo> --parallel <parallel> "<compound_prompt>"`.
- `get_jules_help()`: Introspects the `julius` binary for available commands and error codes.

### JulesSwarmDispatcher

- `from_todo_md(client, repo, todo_path, priority_filter=None)`: Factory method that parses `- [ ]` markdown checklist items from a file. This is the primary bridge between standard project management and massive agent execution.
- `dispatch(parallel=100, batch_size=10)`: Actuates the pre-loaded task pipeline to generate up to hundreds of parallel agent sessions.

### JulesIntegrationAdapter

- `adapt_for_ai_code_editing(prompt, language, **kwargs)`: Invokes Jules specifically geared towards generating raw code assets.
- `adapt_for_llm(messages, model, **kwargs)`: Standardizes Jules into the unified chat message schema (handling `role` and `content`).
- `adapt_for_code_execution(code, language, **kwargs)`: Dispatches code for analysis by Jules, validating output rather than immediately returning raw tokens.

## Swarm Orchestration (Hundreds of Agents)

A major capability of `src/codomyrmex/agents/jules` is the ability to dispatch **hundreds of targeted Jules agents** concurrently and autonomously merge their output.

1. **Configuration**: Agent arrays are configured via massive task lists (often parsed from `TODO.md` via `JulesSwarmDispatcher.from_todo_md`).
2. **Dispatching**: Once loaded, `dispatcher.dispatch(parallel=N)` splits tasks into `batch_size` chunks (e.g., 10 tasks per Jules run), and fires them with a generic parallel ceiling (e.g., `--parallel 100`). This ensures we don't accidentally bottleneck on host system I/O, while offloading LLM complexity to the Jules CLI.
3. **Merging Back In**: Because `julius new` inherently forks branches and creates Pull Requests or commits context directly depending on context, the "merge back in" functionality is seamlessly deferred to native Git/Jules CLI operations. Hundreds of concurrent tasks resolve to structured PRs which Codomyrmex users or GitHub Actions can subsequently merge.

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links

- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
