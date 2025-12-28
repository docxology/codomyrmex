# Codomyrmex Agents — src/codomyrmex/pattern_matching

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing pattern recognition and code analysis capabilities for the Codomyrmex platform. This module identifies patterns, structures, and relationships within the codebase using advanced analysis techniques including embeddings, symbol extraction, and dependency analysis.

The pattern_matching module serves as the intelligence layer for understanding codebase structure and relationships, enabling advanced code analysis and automation features.

## Module Overview

### Key Capabilities
- **Repository Analysis**: Comprehensive analysis of codebases with pattern recognition
- **Embedding Generation**: Text and code embeddings for semantic analysis
- **Symbol Extraction**: Identification and analysis of code symbols and their usage
- **Dependency Analysis**: Mapping of code dependencies and relationships
- **Text Search**: Advanced search capabilities with context extraction
- **Code Summarization**: Automatic generation of code summaries and documentation

### Key Features
- Integration with cased/kit toolkit for advanced analysis
- Support for multiple analysis types and output formats
- Configurable analysis depth and scope
- Integration with logging system for analysis tracking
- Export capabilities for analysis results

## Function Signatures

### Core Analysis Functions

```python
def get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL) -> Callable
```

Get an embedding function for text/code analysis.

**Parameters:**
- `model_name` (str): Name of the embedding model to use. Defaults to DEFAULT_EMBEDDING_MODEL

**Returns:** `Callable` - Embedding function that takes text and returns vector embeddings

```python
def analyze_repository_path(
    repo_path: str,
    analysis_types: list[str] = None,
    output_formats: list[str] = None,
    max_depth: int = 3,
    include_hidden: bool = False,
    verbose: bool = True
) -> dict[str, Any]
```

Perform comprehensive analysis of a repository path.

**Parameters:**
- `repo_path` (str): Path to the repository to analyze
- `analysis_types` (list[str], optional): Types of analysis to perform. If None, performs all available analyses
- `output_formats` (list[str], optional): Output formats for results. If None, uses default formats
- `max_depth` (int): Maximum directory depth for analysis. Defaults to 3
- `include_hidden` (bool): Whether to include hidden files/directories. Defaults to False
- `verbose` (bool): Whether to print progress information. Defaults to True

**Returns:** `dict[str, Any]` - Analysis results organized by analysis type

```python
def run_full_analysis() -> dict[str, Any]
```

Run complete analysis suite on the current repository.

**Returns:** `dict[str, Any]` - Complete analysis results for all supported analysis types

### Specialized Analysis Functions

```python
def _perform_repository_index(
    repo_path: str,
    output_formats: list[str] = None,
    max_depth: int = 3,
    include_hidden: bool = False
) -> dict[str, Any]
```

Index repository structure and metadata.

**Parameters:**
- `repo_path` (str): Path to repository
- `output_formats` (list[str], optional): Output formats
- `max_depth` (int): Maximum depth. Defaults to 3
- `include_hidden` (bool): Include hidden files. Defaults to False

**Returns:** `dict[str, Any]` - Repository index data

```python
def _perform_dependency_analysis(
    repo_path: str,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Analyze code dependencies and relationships.

**Parameters:**
- `repo_path` (str): Path to repository
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Dependency analysis results

```python
def _perform_text_search(
    repo_path: str,
    search_terms: list[str] = None,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Perform text search across repository files.

**Parameters:**
- `repo_path` (str): Path to repository
- `search_terms` (list[str], optional): Terms to search for
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Search results

```python
def _perform_code_summarization(
    repo_path: str,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Generate code summaries and documentation.

**Parameters:**
- `repo_path` (str): Path to repository
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Summarization results

```python
def _perform_docstring_indexing(
    repo_path: str,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Index and analyze docstrings in the codebase.

**Parameters:**
- `repo_path` (str): Path to repository
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Docstring analysis results

```python
def _perform_symbol_extraction(
    repo_path: str,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Extract and analyze code symbols (functions, classes, variables).

**Parameters:**
- `repo_path` (str): Path to repository
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Symbol extraction results

```python
def _perform_symbol_usage_analysis(
    repo_path: str,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Analyze how symbols are used throughout the codebase.

**Parameters:**
- `repo_path` (str): Path to repository
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Symbol usage analysis

```python
def _perform_text_search_context_extraction(
    repo_path: str,
    search_terms: list[str] = None,
    context_lines: int = 3,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Extract contextual information around search terms.

**Parameters:**
- `repo_path` (str): Path to repository
- `search_terms` (list[str], optional): Terms to search for
- `context_lines` (int): Lines of context to extract. Defaults to 3
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Context extraction results

```python
def _perform_chunking_examples(
    repo_path: str,
    output_formats: list[str] = None
) -> dict[str, Any]
```

Generate examples of text/code chunking strategies.

**Parameters:**
- `repo_path` (str): Path to repository
- `output_formats` (list[str], optional): Output formats

**Returns:** `dict[str, Any]` - Chunking examples

### Utility Functions

```python
def print_once(key, message, level="info", _logger=None) -> None
```

Print a message only once per unique key (prevents duplicate output).

**Parameters:**
- `key`: Unique identifier for the message
- `message`: Message to print
- `level` (str): Log level ("info", "warning", "error"). Defaults to "info"
- `_logger`: Optional logger instance

**Returns:** None

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `run_codomyrmex_analysis.py` – Main analysis engine and processing functions

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for analysis operations
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (cased/kit, embedding libraries)
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Analysis Protocols

All pattern analysis within the Codomyrmex platform must:

1. **Respect Repository Boundaries** - Analysis should not access unauthorized files or directories
2. **Handle Large Codebases** - Efficient processing of repositories of any size
3. **Provide Actionable Results** - Analysis results should enable specific improvements
4. **Maintain Performance** - Analysis operations should complete within reasonable time limits
5. **Preserve Privacy** - Analysis should not expose sensitive information

### Module-Specific Guidelines

#### Analysis Execution
- Support configurable analysis depth and scope
- Provide progress indicators for long-running analyses
- Handle various file encodings and formats gracefully
- Generate results in multiple output formats

#### Result Processing
- Structure results for easy consumption by other modules
- Include metadata about analysis parameters and timing
- Support incremental analysis and result caching
- Validate result integrity and consistency

#### Integration Points
- Coordinate with other analysis modules for comprehensive insights
- Share analysis results through standardized interfaces
- Support analysis workflows that combine multiple techniques
- Enable export of results for external consumption

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Related Modules

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Analysis Coordination** - Share analysis results with static_analysis and ai_code_editing modules
2. **Data Provision** - Supply pattern data to data_visualization for analysis visualization
3. **Search Enhancement** - Enhance search capabilities in documentation and git_operations modules
4. **Workflow Integration** - Provide analysis data for project_orchestration workflows

### Quality Gates

Before pattern analysis changes are accepted:

1. **Analysis Accuracy Verified** - Pattern recognition correctly identifies code structures
2. **Performance Validated** - Analysis scales appropriately for repository size
3. **Result Consistency Checked** - Analysis produces consistent results across runs
4. **Security Reviewed** - Analysis doesn't expose sensitive information
5. **Integration Tested** - Results integrate properly with dependent modules

## Version History

- **v0.1.0** (December 2025) - Initial pattern matching system with repository analysis, symbol extraction, and embedding generation capabilities
