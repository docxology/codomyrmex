# Codomyrmex Agents — src/codomyrmex/terminal_interface

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Rich CLI capabilities including colored output, progress bars, interactive prompts, and a custom shell (`codomyrmex>`). Provides cross-platform terminal interface (macOS, Linux, Windows) with table generation, command execution, and beautiful presentation using the `rich` library for consistent terminal rendering.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `interactive_shell.py` – Interactive shell REPL implementation
- `terminal_utils.py` – Terminal formatting and command execution utilities

## Key Classes and Functions

### InteractiveShell (`interactive_shell.py`)
- `InteractiveShell(prompt: str = "codomyrmex> ", **kwargs)` – Initialize interactive shell with custom prompt and configuration
- `start() -> None` – Start the interactive shell session (REPL)
- `execute_command(command: str) -> str` – Execute a single command in the shell
- `default(command: str) -> None` – Default command handler
- `do_help(command: str = None) -> None` – Display help information
- `do_exit() -> bool` – Exit the shell
- `do_quit() -> bool` – Quit the shell (alias for exit)

### TerminalFormatter (`terminal_utils.py`)
- `TerminalFormatter(use_colors: bool = None)` – Utility class for formatting terminal output with colors and styles
- `format(message: str, color: str = None, style: str = None) -> str` – Format message with color and style
- `print_table(data: list, headers: list = None) -> None` – Print data as a formatted table
- `print_success(message: str) -> None` – Print success message
- `print_error(message: str) -> None` – Print error message
- `print_warning(message: str) -> None` – Print warning message
- `print_info(message: str) -> None` – Print info message
- `_supports_color() -> bool` – Check if terminal supports color output

### CommandRunner (`terminal_utils.py`)
- `CommandRunner()` – Utility for running commands with beautiful presentation
- `run(command: str, cwd: Optional[str] = None, capture_output: bool = False) -> CommandResult` – Run a command
- `run_interactive(command: str, cwd: Optional[str] = None) -> int` – Run a command interactively

### Module Exports (`__init__.py`)
- `InteractiveShell` – Interactive shell class
- `TerminalFormatter` – Terminal formatter class
- `CommandRunner` – Command runner class

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation