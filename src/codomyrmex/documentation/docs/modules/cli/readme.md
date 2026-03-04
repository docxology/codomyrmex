# CLI Module - Codomyrmex

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `cli` module provides the primary command-line interface for the Codomyrmex platform. It is built using the `fire` library, allowing for a nested, intuitive command structure. The CLI serves as a unified entry point for all Codomyrmex capabilities, from environment diagnostics to AI-assisted coding and complex workflow orchestration.

## Design Principles

- **Unified Interface**: One command (`codomyrmex`) to rule them all.
- **Zero-Mock Testing**: All CLI handlers and core components are verified with real functional tests.
- **Robust Error Handling**: Graceful degradation when optional modules are missing.
- **Rich Feedback**: Uses `TerminalFormatter` for colored, structured output.
- **Extensibility**: Command handlers are modularized in `src/codomyrmex/cli/handlers/`.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | List available modules and current system status | `codomyrmex modules`, `codomyrmex status` |
| **EXECUTE** | Trigger code generation, workflows, and build operations | `codomyrmex ai`, `codomyrmex workflow run`, `codomyrmex build` |
| **VERIFY** | Confirm environment health and run module tests | `codomyrmex check`, `codomyrmex doctor`, `codomyrmex test <module>` |

PAI agents invoke the CLI as a subprocess to trigger codomyrmex operations. `codomyrmex check` gates Algorithm cycles by verifying environment health. `codomyrmex test <module>` drives VERIFY-phase validation. `codomyrmex ai generate` and `codomyrmex workflow run` are primary EXECUTE-phase entry points.

## Key Python Exports

| Symbol | Description |
|--------|-------------|
| `main` | CLI entry point — the `codomyrmex` command |
| `check_environment` | Verify dependencies and module health |
| `show_modules` | List all available Codomyrmex modules |
| `show_system_status` | Full system status dashboard |
| `run_interactive_shell` | Launch interactive REPL |
| `handle_ai_generate` | AI code generation handler |
| `handle_ai_refactor` | AI code refactoring handler |
| `handle_code_analysis` | Static analysis and linting handler |
| `run_workflow` | Execute a named workflow |
| `handle_module_test` | Run tests for a specific module |
| `handle_skills_sync` | Sync skill definitions from upstream |

## Command Structure

The CLI is organized into several command groups:

### System & Diagnostics
- `codomyrmex info`: Show platform information.
- `codomyrmex check`: Verify environment setup and dependencies.
- `codomyrmex modules`: List all available modules.
- `codomyrmex status`: Show comprehensive system status dashboard.
- `codomyrmex doctor`: Run self-diagnostics on the ecosystem.

### Development Tools
- `codomyrmex ai [generate|refactor]`: AI-powered code operations.
- `codomyrmex analyze [code|git]`: Static code and git history analysis.
- `codomyrmex build project`: Orchestrate build pipelines.
- `codomyrmex test <module_name>`: Run unit tests for a specific module.
- `codomyrmex demo <module_name>`: Run module demonstrations.

### Orchestration & Workflows
- `codomyrmex workflow [list|run|create]`: Manage and execute workflows.
- `codomyrmex project [list|create]`: Project-level management.
- `codomyrmex orchestration [status|health]`: Monitor the orchestration engine.

### Advanced Features
- `codomyrmex fpf [fetch|parse|search|visualize|...]`: First Principles Framework tools.
- `codomyrmex skills [sync|list|get|search]`: Manage agentic skills.
- `codomyrmex chat`: Launch AI-agent conversation loop.
- `codomyrmex shell`: Interactive REPL shell.

### Quick Orchestration
- `codomyrmex run <target>`: Quick run a script or module.
- `codomyrmex pipe <commands>`: Chain commands sequentially.
- `codomyrmex batch <targets>`: Run multiple targets in parallel.

## Directory Layout

- `core.py`: Main CLI entry point and `Cli` class definition.
- `doctor.py`: System diagnostic implementation.
- `handlers/`: Domain-specific command implementations.
- `utils.py`: Shared CLI utilities and formatting.

## Testing

Verified with integrated tests using the Zero-Mock policy:
```bash
uv run pytest src/codomyrmex/tests/unit/cli/test_cli_integrated.py
```

## Navigation

- [Technical Specification](SPEC.md)
- [Agent Guidelines](AGENTS.md)
- [Parent Directory](../README.md)
