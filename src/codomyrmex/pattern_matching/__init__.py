"""
Pattern Matching Module for Codomyrmex.

This module identifies patterns and structures within the Codomyrmex codebase.
It utilizes the `cased/kit` toolkit for code analysis and pattern recognition.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
- get_embedding_function
- analyze_repository_path
- run_full_analysis
- print_once
- _perform_repository_index
- _perform_dependency_analysis
- _perform_text_search
- _perform_code_summarization
- _perform_docstring_indexing
- _perform_symbol_extraction
- _perform_symbol_usage_analysis
- _perform_text_search_context_extraction
- _perform_chunking_examples
"""

from .run_codomyrmex_analysis import (
    _perform_chunking_examples,
    _perform_code_summarization,
    _perform_dependency_analysis,
    _perform_docstring_indexing,
    _perform_repository_index,
    _perform_symbol_extraction,
    _perform_symbol_usage_analysis,
    _perform_text_search,
    _perform_text_search_context_extraction,
    analyze_repository_path,
    get_embedding_function,
    print_once,
    run_full_analysis,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the pattern_matching module."""
    return {
        "patterns": {
            "help": "List known code patterns (repository index, symbols, dependencies, etc.)",
            "handler": lambda **kwargs: print(
                "Known patterns:\n"
                "  - repository_index: Index repository structure\n"
                "  - dependency_analysis: Analyze module dependencies\n"
                "  - text_search: Search for text patterns\n"
                "  - code_summarization: Summarize code blocks\n"
                "  - docstring_indexing: Index docstrings\n"
                "  - symbol_extraction: Extract symbols\n"
                "  - symbol_usage: Analyze symbol usage\n"
                "  - chunking: Chunk code for analysis"
            ),
        },
        "scan": {
            "help": "Scan for patterns at --path (default: current directory)",
            "handler": lambda path=".", **kwargs: print(
                f"Scanning path: {path}\n"
                f"Repository path: {analyze_repository_path(path)}"
            ),
        },
    }


__all__ = [
    "get_embedding_function",
    "analyze_repository_path",
    "run_full_analysis",
    "print_once",
    "_perform_repository_index",
    "_perform_dependency_analysis",
    "_perform_text_search",
    "_perform_code_summarization",
    "_perform_docstring_indexing",
    "_perform_symbol_extraction",
    "_perform_symbol_usage_analysis",
    "_perform_text_search_context_extraction",
    "_perform_chunking_examples",
    "cli_commands",
]
