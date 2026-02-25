"""
Pattern Matching Module for Codomyrmex.

This module identifies patterns and structures within codebases.
It provides AST-based pattern matching, design pattern detection,
code similarity analysis, and general text/regex pattern scanning.

Submodules:
    analysis -- Core pattern analysis (PatternAnalyzer, PatternMatch)
    ast_matcher -- AST-based structural pattern matching
    code_patterns -- Design pattern detection (singleton, factory, observer, etc.)
    similarity -- Code similarity and duplicate detection

Function exports.
    get_embedding_function, analyze_repository_path, run_full_analysis,
    print_once, and _perform_* helpers.
"""

from .ast_matcher import ASTMatcher, ASTMatchResult
from .code_patterns import PATTERNS, PatternDefinition, PatternDetector
from .run_codomyrmex_analysis import (
    AnalysisResult,
    PatternAnalyzer,
    PatternMatch,
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
    run_codomyrmex_analysis,
    run_full_analysis,
)
from .similarity import CodeSimilarity, DuplicateResult

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
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
    # Core analysis
    "PatternAnalyzer",
    "PatternMatch",
    "AnalysisResult",
    "run_codomyrmex_analysis",
    # AST matching
    "ASTMatcher",
    "ASTMatchResult",
    # Design pattern detection
    "PatternDetector",
    "PatternDefinition",
    "PATTERNS",
    # Similarity
    "CodeSimilarity",
    "DuplicateResult",
    # Function exports.
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
