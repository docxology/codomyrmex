# Languages Module Specification

## Architecture

The module uses a unified Manager pattern for each language. Each language resides in a sub-package (e.g., `src/codomyrmex/languages/python/`) and contains a `Manager` class that adheres to a common structural interface, though Duck Typing is used in `mcp_tools.py` for simplicity.

### The Manager Pattern

Each Manager class (e.g., `PythonManager`) MUST implement the following methods:

* `is_installed(self) -> bool`: Executes a lightweight subprocess check (like `python3 --version`) and returns True on 0 exit code.
* `install_instructions(self) -> str`: Returns clear markdown instructions on how a user or agent should install the language via terminal on macOS/Linux.
* `use_script(self, script_content: str, dir_path: str | None = None) -> str`: Write the script to a temporary file (or specific directory), execute it using the installed language toolchain, capture and return `stdout` + `stderr`.
* `setup_project(self, path: str) -> bool`: Perform language-specific initialization (e.g., `uv init`, `npm init -y`) in the given path.

## Zero-Mock Policy

Tests for this module MUST actually run the shell processes if the toolchain is installed.
If a toolchain is not installed on the system running the test, the test may elegantly skip or assert on the expected missing state, but it MUST NOT mock `subprocess`.
