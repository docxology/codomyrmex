"""
Shared utilities for Codomyrmex orchestrator scripts.

This module provides common functions and patterns used across all
orchestrator scripts to ensure consistency and reduce code duplication.

Note: This file is now a thin wrapper around `codomyrmex.utils.cli_helpers`.
Please modify that file for any changes to utility behavior.
"""

from codomyrmex.utils.cli_helpers import (
    ProgressReporter,
    OUTPUT_WIDTH,
    format_table,
    print_progress_bar,
    validate_dry_run,
    enhanced_error_context,
    create_dry_run_plan,
    add_common_arguments,
    print_with_color,
    format_output,
    validate_file_path,
    load_json_file,
    save_json_file,
    print_section,
    print_success,
    print_error,
    print_warning,
    print_info,
    handle_common_exceptions,
    format_result,
    determine_language_from_file,
    ensure_output_directory,
    parse_common_args,
)

__all__ = [
    "ProgressReporter",
    "OUTPUT_WIDTH",
    "format_table",
    "print_progress_bar",
    "validate_dry_run",
    "enhanced_error_context",
    "create_dry_run_plan",
    "add_common_arguments",
    "print_with_color",
    "format_output",
    "validate_file_path",
    "load_json_file",
    "save_json_file",
    "print_section",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "handle_common_exceptions",
    "format_result",
    "determine_language_from_file",
    "ensure_output_directory",
    "parse_common_args",
]
