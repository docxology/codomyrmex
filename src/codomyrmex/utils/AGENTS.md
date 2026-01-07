# Codomyrmex Agents — src/codomyrmex/utils

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
Shared utilities for Codomyrmex orchestrator scripts. Provides common functions and patterns used across all orchestrator scripts to ensure consistency and reduce code duplication.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `cli_helpers.py` – Shared CLI utilities and helpers

## Key Functions
- `ProgressReporter` – Progress reporting utility for long-running operations
  - `update(increment: int = 1, message: Optional[str] = None) -> None`
  - `set_current(current: int, message: Optional[str] = None) -> None`
  - `complete(message: str = "Completed") -> None`
- `format_table(data: List[Dict[str, Any]], headers: List[str]) -> str` – Format data as a table
- `print_progress_bar(current: int, total: int, prefix: str = "Progress") -> None` – Print a simple progress bar
- `validate_dry_run(args: argparse.Namespace) -> bool` – Validate and confirm dry-run mode
- `enhanced_error_context(operation: str, context: Optional[Dict[str, Any]] = None)` – Context manager for enhanced error reporting
- `create_dry_run_plan(args: argparse.Namespace, operations: List[Dict[str, Any]]) -> str` – Create a dry-run execution plan
- `add_common_arguments(parser: argparse.ArgumentParser) -> None` – Add common arguments to argument parser
- `print_with_color(message: str, color: str = "default", **kwargs) -> None` – Print message with color
- `format_output(data: Any, format_type: str = "json", indent: int = 2) -> str` – Format output data consistently
- `validate_file_path(path: Union[str, Path], must_exist: bool = True, must_be_file: bool = False, must_be_dir: bool = False) -> Path` – Validate and normalize a file path
- `load_json_file(path: Union[str, Path]) -> Dict[str, Any]` – Load JSON file with consistent error handling
- `save_json_file(data: Any, path: Union[str, Path], indent: int = 2, create_parents: bool = True) -> Path` – Save data to JSON file
- `print_section(title: str, separator: str = "-", width: int = OUTPUT_WIDTH, prefix: str = "") -> None` – Print a formatted section header
- `print_success(message: str, context: Optional[str] = None) -> None` – Print a success message consistently
- `print_error(message: str, context: Optional[str] = None, exception: Optional[Exception] = None) -> None` – Print an error message consistently
- `print_warning(message: str, context: Optional[str] = None) -> None` – Print a warning message consistently
- `print_info(message: str) -> None` – Print an info message consistently
- `handle_common_exceptions(operation_name: str, context: Optional[str] = None, verbose: bool = False)` – Decorator for handling common exceptions consistently
- `format_result(result: Any, success_key: str = "success", output_key: Optional[str] = None) -> tuple[bool, Optional[str]]` – Extract success status and optional message from result
- `determine_language_from_file(file_path: Union[str, Path]) -> str` – Determine programming language from file extension
- `ensure_output_directory(output_path: Union[str, Path]) -> Path` – Ensure output directory exists
- `parse_common_args(args: Any) -> Dict[str, Any]` – Extract common arguments from argparse namespace

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Provide consistent error handling and output formatting across all orchestrator scripts.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation

