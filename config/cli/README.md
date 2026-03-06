# CLI Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

The CLI module provides the primary command-line interface for the Codomyrmex development platform. Built on Python Fire, it exposes all platform capabilities through a nested subcommand structure including workflow management, project operations, AI code generation, code analysis, FPF (First Principles Framework) operations, skills management, and an interactive REPL shell.

## PAI Integration

| Algorithm Phase | CLI Role |
|----------------|----------|
| EXECUTE | Primary user-facing entry point for invoking platform commands |
| OBSERVE | `codomyrmex status`, `codomyrmex modules`, `codomyrmex doctor` for system inspection |
| VERIFY | `codomyrmex doctor --all` runs self-diagnostics on PAI, MCP, RASP, workflows, and imports |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `main` | function | CLI entry point via Python Fire |
| `check_environment` | function | Verify environment setup and dependencies |
| `show_info` | function | Display platform information |
| `show_modules` | function | List available modules and descriptions |
| `show_system_status` | function | Comprehensive system status dashboard |
| `run_interactive_shell` | function | Launch the codomyrmex REPL shell |
| `handle_workflow_create` | function | Create a new workflow definition |
| `list_workflows` | function | List available workflows |
| `run_workflow` | function | Execute a named workflow |
| `handle_project_create` | function | Initialize a new project |
| `handle_ai_generate` | function | Generate code with AI assistance |
| `handle_ai_refactor` | function | Refactor existing code |
| `handle_code_analysis` | function | Run code analysis and linting |
| `handle_fpf_fetch` | function | Fetch FPF repository data |
| `handle_skills_list` | function | List available skills |

## Quick Start

```python
# Programmatic usage
from codomyrmex.cli import main, check_environment, show_modules

# Run environment check
check_environment()

# List available modules
show_modules()

# CLI usage (from terminal)
# codomyrmex check
# codomyrmex modules
# codomyrmex doctor --all
# codomyrmex shell
# codomyrmex workflow list
# codomyrmex ai generate "Create a REST endpoint" --language python
```

## Architecture

```
cli/
  __init__.py          # Module exports (main + 40 handler functions)
  core.py              # Cli class (Python Fire entry point)
  doctor.py            # Self-diagnostic checks (PAI, MCP, RASP, workflows, imports)
  commands.py          # Command definitions
  completion.py        # Shell completion support
  utils.py             # Shared utilities (logger, performance monitoring check)
  mcp_tools.py         # MCP tool definitions (cli_list_commands, cli_run_command)
  handlers/            # Command handler implementations
    ai.py              # AI generate and refactor handlers
    analysis.py        # Code and git analysis handlers
    chat.py            # Infinite conversation / dev_loop handler
    demos.py           # Module demonstration handlers
    fpf.py             # FPF fetch/parse/export/search/visualize handlers
    orchestration.py   # Orchestration status and health handlers
    quick.py           # Quick run/pipe/batch handlers
    skills.py          # Skills sync/list/get/search handlers
    system.py          # System info/modules/status/shell handlers
  completions/         # Shell completion scripts
  formatters/          # Output formatting utilities
  parsers/             # Input parsing utilities
  themes/              # Terminal color themes
```

## MCP Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `cli_list_commands` | List all available CLI commands by introspecting the Cli class | None |
| `cli_run_command` | Execute a CLI command by name | `command` (str), `args` (JSON string, optional) |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/cli/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) -- Agent coordination documentation
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../src/codomyrmex/cli/)
