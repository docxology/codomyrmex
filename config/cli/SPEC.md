# CLI Module - Technical Specification

**Version**: v1.1.9 | **Last Updated**: March 2026

## Overview

The CLI module provides Codomyrmex's command-line interface, built on Python Fire for automatic CLI generation from class methods. It supports nested subcommand groups, interactive shell mode, self-diagnostics, and MCP tool exposure for agent-driven command execution.

## Design Principles

- **Zero-Mock Policy**: Tests use real CLI invocations, no mocked command handlers.
- **Explicit Failure**: All handlers raise exceptions on error; no silent fallbacks or placeholder returns.
- **Fire-Based Auto-Discovery**: The `Cli` class structure directly maps to the CLI command hierarchy -- nested classes become subcommand groups automatically.

## Architecture

```
cli/
  __init__.py          # Public API: main + 40 handler functions
  core.py              # Cli class (Python Fire entry point)
  doctor.py            # Self-diagnostic framework (CheckResult, run_doctor)
  commands.py          # Command definitions
  completion.py        # Shell completion
  utils.py             # Logger, performance monitoring flag
  mcp_tools.py         # cli_list_commands, cli_run_command
  handlers/
    __init__.py        # Re-exports all handler functions
    ai.py              # handle_ai_generate, handle_ai_refactor
    analysis.py        # handle_code_analysis, handle_git_analysis
    chat.py            # handle_chat_session (infinite conversation)
    demos.py           # demo_data_visualization, demo_code_execution, etc.
    fpf.py             # 8 FPF handlers (fetch, parse, export, search, visualize, context, analyze, report)
    orchestration.py   # handle_orchestration_status, handle_orchestration_health
    quick.py           # handle_quick_run, handle_quick_pipe, handle_quick_batch, handle_quick_chain, handle_quick_workflow
    skills.py          # handle_skills_sync, handle_skills_list, handle_skills_get, handle_skills_search
    system.py          # check_environment, show_info, show_modules, show_system_status, run_interactive_shell
  completions/         # Shell completion scripts
  formatters/          # Output formatting
  parsers/             # Input parsing
  themes/              # Terminal themes
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
# Main entry point
class Cli:
    def __init__(self, verbose: bool = False, performance: bool = False): ...
    def check(self) -> Any: ...
    def info(self) -> Any: ...
    def modules(self) -> Any: ...
    def status(self) -> Any: ...
    def shell(self) -> Any: ...
    def doctor(self, pai=False, mcp=False, rasp=False, workflows=False,
               imports=False, all_checks=False, output_json=False) -> int: ...
    def test(self, module_name: str) -> Any: ...
    def demo(self, module_name: str) -> Any: ...
    def run(self, target, args=None, timeout=60, parallel=False, verbose=False) -> Any: ...
    def pipe(self, commands, continue_on_error=False) -> Any: ...
    def batch(self, targets, workers=4, timeout=60, verbose=False) -> Any: ...

# Nested subcommand classes
class Cli.workflow:
    def list(self) -> Any: ...
    def run(self, name: str, params: str = "") -> Any: ...
    def create(self, name: str, template: str = "") -> Any: ...

class Cli.project:
    def list(self) -> Any: ...
    def create(self, name: str, template: str = "ai_analysis",
               description: str = "", path: str = "") -> Any: ...

class Cli.ai:
    def generate(self, prompt: str, language: str = "python",
                 provider: str = "openai") -> Any: ...
    def refactor(self, file: str, instruction: str) -> Any: ...

# Doctor diagnostics
class CheckResult:
    OK: str = "ok"
    WARN: str = "warn"
    ERROR: str = "error"
    def __init__(self, name: str, status: str = OK,
                 message: str = "", details: dict | None = None): ...
```

## Dependencies

**Internal**: `codomyrmex.performance`, `codomyrmex.logging_monitoring`, `codomyrmex.utils.cli_helpers`, `codomyrmex.model_context_protocol.decorators`

**External**: `fire` (Python Fire)

## Constraints

- Python Fire generates the CLI from class structure -- method signatures determine argument parsing.
- The `doctor` command traverses the filesystem to locate RASP docs and workflow files.
- MCP tools (`cli_run_command`) instantiate a fresh `Cli()` per invocation.

## Navigation

- [README.md](README.md) -- Module overview
- [AGENTS.md](AGENTS.md) -- Agent coordination
- [Source Module](../../src/codomyrmex/cli/)
