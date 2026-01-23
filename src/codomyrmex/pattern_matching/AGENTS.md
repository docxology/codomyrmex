# Codomyrmex Agents — src/codomyrmex/pattern_matching

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Pattern Matching module provides code pattern recognition and analysis capabilities for the Codomyrmex codebase. It identifies patterns, structures, and code relationships within repositories using the `cased/kit` toolkit approach. The module supports repository indexing, dependency analysis, text search, code summarization, docstring indexing, and symbol extraction for comprehensive codebase understanding.

## Active Components

### Core Analysis

- `run_codomyrmex_analysis.py` - Main pattern matching analysis runner
  - Key Classes: `PatternAnalyzer`, `PatternMatch`, `AnalysisResult`
  - Key Functions: `run_codomyrmex_analysis()`, `analyze_repository_path()`, `run_full_analysis()`, `get_embedding_function()`

### Pattern Recognition

- `PatternAnalyzer` - Core class for analyzing code patterns
  - Methods: `analyze_file()`, `analyze_directory()`

### Analysis Operations

- `_perform_repository_index()` - Index repository contents
- `_perform_dependency_analysis()` - Analyze code dependencies
- `_perform_text_search()` - Search for text patterns
- `_perform_code_summarization()` - Generate code summaries
- `_perform_docstring_indexing()` - Index documentation strings
- `_perform_symbol_extraction()` - Extract code symbols
- `_perform_symbol_usage_analysis()` - Analyze symbol usage patterns
- `_perform_text_search_context_extraction()` - Extract search context
- `_perform_chunking_examples()` - Demonstrate text chunking

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `PatternAnalyzer` | run_codomyrmex_analysis | Main class for pattern analysis |
| `PatternMatch` | run_codomyrmex_analysis | Dataclass representing a pattern match |
| `AnalysisResult` | run_codomyrmex_analysis | Dataclass for analysis results |
| `run_codomyrmex_analysis()` | run_codomyrmex_analysis | Run pattern analysis on a directory |
| `analyze_repository_path()` | run_codomyrmex_analysis | Analyze a repository path |
| `run_full_analysis()` | run_codomyrmex_analysis | Run complete analysis sequence |
| `get_embedding_function()` | run_codomyrmex_analysis | Get embedding function for analysis |
| `analyze_file()` | PatternAnalyzer | Analyze single file for patterns |
| `analyze_directory()` | PatternAnalyzer | Analyze directory recursively |
| `_perform_repository_index()` | run_codomyrmex_analysis | Index repository for searching |
| `_perform_dependency_analysis()` | run_codomyrmex_analysis | Analyze code dependencies |
| `_perform_text_search()` | run_codomyrmex_analysis | Perform text pattern search |
| `_perform_code_summarization()` | run_codomyrmex_analysis | Generate code summaries |
| `_perform_docstring_indexing()` | run_codomyrmex_analysis | Index docstrings for search |
| `_perform_symbol_extraction()` | run_codomyrmex_analysis | Extract symbols from code |
| `_perform_symbol_usage_analysis()` | run_codomyrmex_analysis | Analyze symbol usage patterns |
| `print_once()` | run_codomyrmex_analysis | Utility for single-print messages |

## Operating Contracts

1. **Logging**: All analysis operations use `logging_monitoring` for structured logging
2. **File Extensions**: Default analysis targets `.py`, `.js`, `.ts` files (configurable)
3. **Pattern Format**: Patterns are defined as string-based search patterns
4. **Results Structure**: Analysis returns `AnalysisResult` with matches, errors, and file counts
5. **Error Handling**: File reading errors are logged and collected in result errors list
6. **Encoding**: Files are read with UTF-8 encoding, ignoring decode errors

## Integration Points

- **logging_monitoring** - All analysis functions log via centralized logger
- **environment_setup** - Dependency checking at application startup
- **static_analysis** - Complementary code analysis capabilities
- **cerebrum** - Code understanding and reasoning integration

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| static_analysis | [../static_analysis/AGENTS.md](../static_analysis/AGENTS.md) | Static code analysis |
| cerebrum | [../cerebrum/AGENTS.md](../cerebrum/AGENTS.md) | Reasoning engine |
| coding | [../coding/AGENTS.md](../coding/AGENTS.md) | Code execution |
| documentation | [../documentation/AGENTS.md](../documentation/AGENTS.md) | Documentation generation |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Usage examples
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
