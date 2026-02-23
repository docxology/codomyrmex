# CLI Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Command-line interface module serving as the primary entry point for user interaction with the Codomyrmex platform. Built on argparse, it provides commands for environment checking, module listing, system status, interactive shell mode, workflow management, project operations, AI-assisted code generation and refactoring, code and git analysis, build operations, FPF (Fetch/Parse/Format) data pipelines, and skills management. Each command group is implemented as a handler function dispatched from the central argument parser.

## Key Exports

### Entry Point
- **`main()`** -- Primary CLI entry point that parses arguments and dispatches to the appropriate handler

### Environment and System
- **`check_environment()`** -- Verifies environment setup, dependencies, and configuration
- **`show_info()`** -- Displays platform version and configuration information
- **`show_modules()`** -- Lists all available modules and their status
- **`show_system_status()`** -- Shows system status dashboard with health indicators

### Interactive Shell
- **`run_interactive_shell()`** -- Launches the interactive `codomyrmex>` REPL shell

### Workflow Management
- **`handle_workflow_create()`** -- Creates a new workflow definition
- **`list_workflows()`** -- Lists all available workflow definitions
- **`run_workflow()`** -- Executes a specified workflow

### Project Operations
- **`handle_project_create()`** -- Initializes a new project with scaffolding
- **`handle_project_list()`** -- Lists available projects
- **`handle_orchestration_status()`** -- Shows orchestration pipeline status
- **`handle_orchestration_health()`** -- Reports orchestration system health

### AI Code Operations
- **`handle_ai_generate()`** -- Generates code using AI assistance
- **`handle_ai_refactor()`** -- Refactors existing code with AI guidance

### Code Analysis
- **`handle_code_analysis()`** -- Runs static analysis and linting on source code
- **`handle_git_analysis()`** -- Analyzes git history, patterns, and commit statistics

### Build and Test
- **`handle_project_build()`** -- Builds project artifacts
- **`handle_module_test()`** -- Runs tests for a specific module
- **`handle_module_demo()`** -- Runs demonstration scripts for a module

### FPF (Fetch/Parse/Format)
- **`handle_fpf_fetch()`** -- Fetches FPF data from a URL
- **`handle_fpf_parse()`** -- Parses FPF documents into structured data
- **`handle_fpf_export()`** -- Exports FPF data to various formats
- **`handle_fpf_search()`** -- Searches FPF content
- **`handle_fpf_visualize()`** -- Generates visualizations from FPF data
- **`handle_fpf_context()`** -- Manages FPF context for operations
- **`handle_fpf_export_section()`** -- Exports a specific section of FPF data
- **`handle_fpf_analyze()`** -- Analyzes FPF data structures
- **`handle_fpf_report()`** -- Generates FPF reports

### Skills Management
- **`handle_skills_sync()`** -- Synchronizes skill definitions
- **`handle_skills_list()`** -- Lists available skills
- **`handle_skills_get()`** -- Retrieves details for a specific skill
- **`handle_skills_search()`** -- Searches skills by keyword or tag

### Demos
- **`demo_data_visualization()`** -- Demonstrates data visualization capabilities
- **`demo_ai_code_editing()`** -- Demonstrates AI code editing features
- **`demo_code_execution()`** -- Demonstrates sandboxed code execution
- **`demo_git_operations()`** -- Demonstrates git operation automation

## Directory Contents

- `core.py` -- Main CLI entry point with argparse configuration and handler dispatch
- `__main__.py` -- Allows `python -m codomyrmex.cli` execution
- `handlers/` -- Command handler implementations organized by command group
- `parsers/` -- Argument parser definitions and subcommand configuration
- `formatters/` -- Output formatting utilities for CLI responses
- `completions/` -- Shell completion scripts and providers
- `themes/` -- Terminal color themes and styling configuration
- `utils.py` -- Shared CLI utilities (logger setup, terminal formatting, feature detection)

## Quick Start

```python
from codomyrmex.cli import main, get_formatter

# Enhanced main CLI entry point with comprehensive functionality.
result = main()

# Get TerminalFormatter if available.
output = get_formatter()
```

## Navigation

- **Full Documentation**: [docs/modules/cli/](../../../docs/modules/cli/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
