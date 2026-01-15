# Codomyrmex Agents — cli

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Command-line interface for the Codomyrmex platform, providing access to all modules and workflows.

## Active Components

- `__init__.py` – Module exports
- `__main__.py` – Module entry point
- `core.py` – Main CLI implementation with argparse
- `utils.py` – CLI utilities and terminal formatters
- `handlers/` – Command handler implementations
  - `ai.py` – AI command handlers
  - `analysis.py` – Analysis command handlers
  - `build.py` – Build command handlers
  - `environment.py` – Environment command handlers
  - `fpf.py` – FPF command handlers
  - `skills.py` – Skills command handlers

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure all command handlers use the centralized logging from `logging_monitoring`.
- Commands should fail gracefully with helpful error messages.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
