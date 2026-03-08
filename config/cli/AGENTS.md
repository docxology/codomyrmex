# CLI Module - Agent Coordination

**Version**: v1.1.9 | **Last Updated**: March 2026

## Overview

The CLI module is the primary user-facing entry point for Codomyrmex. Agents interact with it through MCP tools (`cli_list_commands`, `cli_run_command`) or by invoking handler functions directly. The `Cli` class exposes nested subcommand groups (workflow, project, ai, analyze, build, fpf, skills) via Python Fire.

## Key Files

| File | Class/Function | Role |
|------|---------------|------|
| `core.py` | `Cli` | Main CLI class with nested subcommand classes |
| `core.py` | `Cli.doctor()` | Self-diagnostics (PAI, MCP, RASP, workflows, imports) |
| `core.py` | `Cli.shell()` | Interactive REPL shell launcher |
| `doctor.py` | `CheckResult`, `run_doctor()` | Diagnostic check framework and runner |
| `mcp_tools.py` | `cli_list_commands()` | MCP tool: enumerate available CLI commands |
| `mcp_tools.py` | `cli_run_command()` | MCP tool: execute a CLI command by name |
| `handlers/system.py` | `show_modules()`, `show_system_status()` | System inspection handlers |
| `handlers/ai.py` | `handle_ai_generate()`, `handle_ai_refactor()` | AI code operation handlers |
| `handlers/quick.py` | `handle_quick_run()`, `handle_quick_batch()` | Fast script execution handlers |
| `utils.py` | `get_logger()`, `PERFORMANCE_MONITORING_AVAILABLE` | Shared utilities |

## MCP Tools Available

| Tool | Category | Description |
|------|----------|-------------|
| `cli_list_commands` | cli | List all available CLI commands from the Cli class |
| `cli_run_command` | cli | Execute a named CLI command with optional JSON arguments |

## Agent Instructions

1. Use `cli_list_commands` to discover available commands before attempting execution.
2. Use `cli_run_command` with the `command` parameter matching method names on the `Cli` class (e.g., `"check"`, `"modules"`, `"status"`).
3. For subcommands, use dot notation or nested JSON args -- e.g., command `"workflow"` is a nested class, so invoke specific methods like `list_workflows` directly.
4. The `doctor` command accepts flags `--pai`, `--mcp`, `--rasp`, `--workflows`, `--imports`, `--all` for targeted diagnostics.
5. All handlers return structured data or print formatted output; error conditions raise exceptions rather than returning silent failures.

## Operating Contracts

- The `Cli` class requires `fire` (Python Fire) as a runtime dependency.
- Verbose mode (`--verbose`) sets logger to DEBUG level.
- Performance monitoring (`--performance`) is conditional on `codomyrmex.performance` availability.
- The `doctor` command returns exit code 0 (pass), 1 (warnings), or 2 (errors).
- All command handlers are importable from `codomyrmex.cli` directly.

## Common Patterns

```python
# Discover commands via MCP
from codomyrmex.cli.mcp_tools import cli_list_commands, cli_run_command

commands = cli_list_commands()
# {'status': 'success', 'command_count': N, 'commands': [...]}

result = cli_run_command(command="check")
# {'status': 'success', 'command': 'check', 'result': ...}

# Direct handler invocation
from codomyrmex.cli import check_environment, show_modules
check_environment()
show_modules()
```

## PAI Agent Role Access Matrix

| Agent | Access Level | Primary Tools |
|-------|-------------|---------------|
| Engineer | Full | `cli_run_command`, `cli_list_commands`, all handlers |
| Architect | Read | `cli_list_commands`, `show_modules`, `show_system_status` |
| QATester | Execute | `cli_run_command` (test, doctor commands) |

## Navigation

- [README.md](README.md) -- Module overview
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../src/codomyrmex/cli/)
