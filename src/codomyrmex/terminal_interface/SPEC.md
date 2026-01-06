# terminal_interface - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `terminal_interface` module provides rich CLI capabilities: colored output, progress bars, interactive prompts, and a custom shell (`codomyrmex>`).

## Design Principles

### Modularity
- **Formatter/Parser**: Separate modules for styling and input.
- **`rich` Library**: Leverages `rich` for consistent terminal rendering.

### Functionality
- **Cross-Platform**: Works on macOS, Linux, and Windows terminals.

## Functional Requirements

1.  **Interactive Shell**: A REPL for system commands.
2.  **Output Formatting**: Tables, messages, progress bars.
3.  **Input Handling**: Prompts, menus, validation.

## Interface Contracts

- `InteractiveShell`: The REPL host class.
- `terminal_utils`: Functions for `print_table`, `print_success`, etc.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

- **Parent**: [../SPEC.md](../SPEC.md)
