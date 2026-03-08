# CLI Module - Technical Specification

**Version**: v1.1.9 | **Last Updated**: March 2026

## Overview

The CLI module provides the Codomyrmex command-line interface, built on Python Fire for automatic CLI generation from class methods. It supports nested subcommand groups, interactive shell mode, self-diagnostics, and MCP tool exposure.

## Design Principles

- **Zero-Mock Policy**: Tests use real CLI invocations, no mocked command handlers.
- **Explicit Failure**: All handlers raise exceptions on error; no silent fallbacks.
- **Fire-Based Auto-Discovery**: The `Cli` class structure maps directly to the CLI command hierarchy.

## Architecture

```
cli/
  __init__.py       # Public API: main + 40 handler functions
  core.py           # Cli class (Python Fire entry point)
  doctor.py         # Self-diagnostic framework (CheckResult, run_doctor)
  commands.py       # Command definitions
  completion.py     # Shell completion
  utils.py          # Logger, performance monitoring flag
  mcp_tools.py      # cli_list_commands, cli_run_command
  handlers/         # Command handler implementations (9 files)
  completions/      # Shell completion scripts
  formatters/       # Output formatting
  parsers/          # Input parsing
  themes/           # Terminal themes
```

## Functional Requirements

1. Provide a unified CLI entry point via the `codomyrmex` command.
2. Support nested subcommand groups: workflow, project, ai, analyze, build, fpf, skills, orchestration.
3. Launch an interactive REPL shell via `codomyrmex shell`.
4. Run self-diagnostics via `codomyrmex doctor` with granular check flags.
5. Expose CLI capabilities as MCP tools for agent consumption.
6. Support verbose and performance monitoring modes via global flags.
7. Provide quick execution commands (run, pipe, batch) for script orchestration.

## Interface Contracts

```python
class Cli:
    def __init__(self, verbose: bool = False, performance: bool = False): ...
    def check(self) -> Any: ...
    def modules(self) -> Any: ...
    def status(self) -> Any: ...
    def shell(self) -> Any: ...
    def doctor(self, pai=False, mcp=False, rasp=False, workflows=False,
               imports=False, all_checks=False, output_json=False) -> int: ...
    def run(self, target, args=None, timeout=60, parallel=False, verbose=False) -> Any: ...

class CheckResult:
    OK: str = "ok"
    WARN: str = "warn"
    ERROR: str = "error"
```

## Dependencies

**Internal**: `codomyrmex.performance`, `codomyrmex.logging_monitoring`, `codomyrmex.utils.cli_helpers`, `codomyrmex.model_context_protocol.decorators`

**External**: `fire` (Python Fire)

## Constraints

- Python Fire generates the CLI from class structure; method signatures determine argument parsing.
- MCP tools (`cli_run_command`) instantiate a fresh `Cli()` per invocation.

## Navigation

- [readme.md](readme.md) -- Module overview
- [AGENTS.md](AGENTS.md) -- Agent coordination
- [Source Module](../../../../cli/)
