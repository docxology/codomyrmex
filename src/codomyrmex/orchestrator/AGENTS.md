# Codomyrmex Agents — src/codomyrmex/orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Script orchestration module for discovering, configuring, executing, and reporting on Python scripts within the Codomyrmex project.

## Active Components

- `__init__.py` – Module exports: `run_orchestrator`, `load_config`, `get_script_config`
- `core.py` – Main entry point with `main()` function for script orchestration
- `config.py` – Configuration loading with `load_config()`, `get_script_config()`
- `discovery.py` – Script discovery with `discover_scripts()`, `SKIP_DIRS`, `SKIP_PATTERNS`
- `runner.py` – Script execution with `run_script()` function
- `reporting.py` – Reporting with `save_log()`, `generate_report()`, `generate_script_documentation()`
- `README.md` – Human-readable documentation
- `SPEC.md` – Functional specification

## Operating Contracts

- Integrates with `logging_monitoring` for structured logging.
- Uses `utils.cli_helpers` for terminal output formatting.
- Discovers scripts in directory trees with configurable depth and exclusion filters.
- Executes scripts via subprocess with timeout and environment control.
- Generates JSON logs and Markdown reports.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation
