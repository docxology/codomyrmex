# terminal_interface

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Interactive terminal interface module providing shells, command processing, output rendering, and tab-completion for the Codomyrmex platform. Serves as the foundation layer for all terminal-based user interactions, offering an interactive shell mode (`codomyrmex>`), command execution utilities, rich terminal formatting, and autocomplete support. Optional utilities include `CommandRunner` for subprocess management and `TerminalFormatter` for styled output.

## Key Exports

### Submodules
- **`shells`** -- Interactive shell implementations including the main `InteractiveShell` REPL
- **`commands`** -- Command definitions and dispatch logic for shell commands
- **`rendering`** -- Terminal output rendering (colored text, tables, progress indicators)
- **`completions`** -- Tab-completion providers for shell commands and arguments

### Optional Classes (available when dependencies are installed)
- **`InteractiveShell`** -- REPL-style interactive shell with command history, prompt customization, and integrated help
- **`CommandRunner`** -- Subprocess execution utility with timeout support and output capture
- **`TerminalFormatter`** -- Rich text formatting for terminal output (colors, bold, tables, status indicators)

## Directory Contents

- `shells/` -- Interactive shell implementations (InteractiveShell REPL)
- `commands/` -- Command definitions and dispatch handlers
- `rendering/` -- Output rendering utilities (colors, tables, progress bars)
- `completions/` -- Tab-completion providers and argument suggestion logic
- `utils/` -- Optional utilities including CommandRunner and TerminalFormatter

## Navigation

- **Full Documentation**: [docs/modules/terminal_interface/](../../../docs/modules/terminal_interface/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
