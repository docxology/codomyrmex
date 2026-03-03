# CLI Module - Agent Coordination

**Version**: v1.0.8 | **Last Updated**: March 2026

## Overview

The CLI module is the primary user-facing entry point for Codomyrmex. Agents interact with it through MCP tools (`cli_list_commands`, `cli_run_command`) or by invoking handler functions directly. The `Cli` class exposes nested subcommand groups via Python Fire.

## Key Files

| File | Class/Function | Role |
|------|---------------|------|
| `core.py` | `Cli` | Main CLI class with nested subcommand classes |
| `core.py` | `Cli.doctor()` | Self-diagnostics (PAI, MCP, RASP, workflows, imports) |
| `doctor.py` | `CheckResult`, `run_doctor()` | Diagnostic check framework and runner |
| `mcp_tools.py` | `cli_list_commands()` | MCP tool: enumerate available CLI commands |
| `mcp_tools.py` | `cli_run_command()` | MCP tool: execute a CLI command by name |
| `handlers/system.py` | `show_modules()`, `show_system_status()` | System inspection handlers |
| `handlers/ai.py` | `handle_ai_generate()`, `handle_ai_refactor()` | AI code operation handlers |
| `handlers/quick.py` | `handle_quick_run()`, `handle_quick_batch()` | Fast script execution handlers |

## MCP Tools Available

| Tool | Category | Description |
|------|----------|-------------|
| `cli_list_commands` | cli | List all available CLI commands from the Cli class |
| `cli_run_command` | cli | Execute a named CLI command with optional JSON arguments |

## Agent Instructions

1. Use `cli_list_commands` to discover available commands before attempting execution.
2. Use `cli_run_command` with the `command` parameter matching method names on the `Cli` class (e.g., `"check"`, `"modules"`, `"status"`).
3. The `doctor` command accepts flags `--pai`, `--mcp`, `--rasp`, `--workflows`, `--imports`, `--all` for targeted diagnostics.
4. All handlers return structured data or print formatted output; error conditions raise exceptions rather than returning silent failures.

## Operating Contracts

- The `Cli` class requires `fire` (Python Fire) as a runtime dependency.
- Verbose mode (`--verbose`) sets logger to DEBUG level.
- The `doctor` command returns exit code 0 (pass), 1 (warnings), or 2 (errors).

## Common Patterns

```python
from codomyrmex.cli.mcp_tools import cli_list_commands, cli_run_command

commands = cli_list_commands()
result = cli_run_command(command="check")
```

## PAI Agent Role Access Matrix

| Agent | Access Level | Primary Tools |
|-------|-------------|---------------|
| Engineer | Full | `cli_run_command`, `cli_list_commands`, all handlers |
| Architect | Read | `cli_list_commands`, `show_modules`, `show_system_status` |
| QATester | Execute | `cli_run_command` (test, doctor commands) |

## Navigation

- [readme.md](readme.md) -- Module overview
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../cli/)
