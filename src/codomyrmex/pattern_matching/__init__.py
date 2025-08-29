"""
Pattern Matching Module for Codomyrmex.

This module focuses on identifying specific patterns and structures within the
Codomyrmex codebase. It extensively utilizes the `cased/kit` toolkit for
comprehensive code analysis and pattern recognition.

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
    get_embedding_function,
    analyze_repository_path,
    run_full_analysis,
    print_once,
    _perform_repository_index,
    _perform_dependency_analysis,
    _perform_text_search,
    _perform_code_summarization,
    _perform_docstring_indexing,
    _perform_symbol_extraction,
    _perform_symbol_usage_analysis,
    _perform_text_search_context_extraction,
    _perform_chunking_examples,
)

__all__ = [
    'get_embedding_function',
    'analyze_repository_path',
    'run_full_analysis',
    'print_once',
    '_perform_repository_index',
    '_perform_dependency_analysis',
    '_perform_text_search',
    '_perform_code_summarization',
    '_perform_docstring_indexing',
    '_perform_symbol_extraction',
    '_perform_symbol_usage_analysis',
    '_perform_text_search_context_extraction',
    '_perform_chunking_examples',
] 