# Codomyrmex Agents - src/codomyrmex/cli

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The CLI module provides the command-line interface for Codomyrmex - the enhanced modular coding workspace. It offers comprehensive commands for environment management, workflow orchestration, project management, AI operations, code analysis, build operations, FPF (First Principles Framework) operations, and skills management.

## Active Components

- `__init__.py` - Module exports for main function and all handlers
- `__main__.py` - Entry point for `python -m codomyrmex.cli`
- `core.py` - Main CLI implementation with argparse configuration and command routing
- `utils.py` - CLI utility functions (logging, formatting, availability checks)
- `handlers/` - Command handler implementations organized by domain
  - `system.py` - Environment, info, modules, status, shell commands
  - `orchestration.py` - Workflow and project management, orchestration status
  - `ai.py` - AI generate and refactor commands
  - `analysis.py` - Code and git analysis commands
  - `demos.py` - Module demos (data visualization, AI code editing, code execution, git operations)
  - `fpf.py` - First Principles Framework commands (fetch, parse, export, search, visualize, context, analyze, report)
  - `skills.py` - Skills management (sync, list, get, search)

## Key Classes

- **main()** - Primary CLI entry point with argparse command routing
- **ProgressReporter** (from utils) - Progress bar utility for long operations
- **TerminalFormatter** (optional) - Rich terminal formatting when available
- **PerformanceMonitor** (optional) - Performance monitoring when enabled

## Operating Contracts

- Commands are organized hierarchically: `codomyrmex <group> <action> [args]`
- Global options: `--verbose/-v` for debug output, `--performance/-p` for monitoring
- Command groups: check, info, modules, status, shell, workflow, project, orchestration, ai, analyze, build, module, fpf, skills
- Handlers return boolean success status; exit code is 0 for success, 1 for failure
- Verbose mode enables DEBUG logging level
- Performance monitoring integrates with `codomyrmex.performance` module when available

## Signposting

- **Parent Directory**: [codomyrmex](../README.md) - Main package documentation
- **Handler Modules**:
  - [handlers/](./handlers/README.md) - Command handler implementations
- **Related Modules**:
  - [utils/](../utils/README.md) - Shared utility functions
  - [performance/](../performance/README.md) - Performance monitoring
  - [terminal_interface/](../terminal_interface/README.md) - Terminal formatting
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
