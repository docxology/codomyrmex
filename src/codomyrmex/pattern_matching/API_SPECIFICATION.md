# Pattern Matching - API Specification

## Introduction

The Pattern Matching module provides comprehensive code analysis and pattern recognition capabilities using the `cased/kit` toolkit. This API enables developers to search for text patterns, analyze symbol usage, perform semantic searches, and extract comprehensive repository information.

## Core Functions

### Function 1: `get_embedding_function(model_name: str = "all-MiniLM-L6-v2")`

- **Description**: Retrieves or creates an embedding function for semantic analysis. Uses SentenceTransformer to generate vector embeddings for text-based semantic search.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `model_name` (str, optional): Name of the SentenceTransformer model to use. Default: `"all-MiniLM-L6-v2"`.
- **Returns/Response**:
    - Returns a callable function that takes a string and returns a list of floats (embedding vector), or `None` if initialization fails.
- **Events Emitted**: N/A
- **Example**:
    ```python
    from codomyrmex.pattern_matching import get_embedding_function

    embed_fn = get_embedding_function()
    if embed_fn:
        vector = embed_fn("example code snippet")
        print(f"Embedding dimension: {len(vector)}")
    ```

### Function 2: `analyze_repository_path(repo_path: str, output_dir: str = "./output/codomyrmex_analysis")`

- **Description**: Analyzes a single repository path using `cased/kit` Repository object. Performs basic repository indexing and analysis.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `repo_path` (str): Path to the repository directory to analyze.
    - `output_dir` (str, optional): Directory where analysis results will be saved. Default: `"./output/codomyrmex_analysis"`.
- **Returns/Response**:
    - Returns a `Repository` object from `cased/kit` that can be used for further analysis operations.
- **Events Emitted**: N/A
- **Example**:
    ```python
    from codomyrmex.pattern_matching import analyze_repository_path

    repo = analyze_repository_path("./src/codomyrmex", output_dir="./analysis_output")
    ```

### Function 3: `run_full_analysis(repo_paths: list[str] = None, output_dir: str = "./output/codomyrmex_analysis")`

- **Description**: Performs comprehensive analysis across multiple repository paths. Executes all configured analysis stages including repository indexing, dependency analysis, text search, code summarization, docstring indexing, symbol extraction, symbol usage analysis, and context extraction.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `repo_paths` (list[str], optional): List of repository paths to analyze. If None, uses default paths from the module configuration.
    - `output_dir` (str, optional): Directory where all analysis results will be saved. Default: `"./output/codomyrmex_analysis"`.
- **Returns/Response**:
    - Returns a dictionary containing analysis results and metadata.
- **Events Emitted**: N/A
- **Example**:
    ```python
    from codomyrmex.pattern_matching import run_full_analysis

    results = run_full_analysis(
        repo_paths=["./src/codomyrmex", "./examples"],
        output_dir="./comprehensive_analysis"
    )
    ```

### Function 4: `print_once(key: str, message: str)`

- **Description**: Utility function that prints a message only once per unique key. Useful for avoiding duplicate log messages or warnings.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `key` (str): Unique identifier for the message.
    - `message` (str): Message to print.
- **Returns/Response**: None
- **Events Emitted**: N/A

## Internal Analysis Functions

These functions are available for programmatic use but are primarily called internally by `run_full_analysis()`:

### Function 5: `_perform_repository_index(repo: Repository, output_dir: Path) -> dict`

- **Description**: Creates an index of the repository structure and saves metadata.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with indexing results.

### Function 6: `_perform_dependency_analysis(repo: Repository, output_dir: Path) -> dict`

- **Description**: Analyzes Python dependencies and creates dependency graphs.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with dependency analysis results.

### Function 7: `_perform_text_search(repo: Repository, queries: list[str], output_dir: Path) -> dict`

- **Description**: Searches for text patterns or regular expressions across the repository.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `queries` (list[str]): List of text patterns or regex queries to search for.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with text search results.

### Function 8: `_perform_code_summarization(repo: Repository, output_dir: Path) -> dict`

- **Description**: Generates LLM-based summaries of code files.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with summarization results.

### Function 9: `_perform_docstring_indexing(repo: Repository, output_dir: Path) -> dict`

- **Description**: Creates a searchable index of docstrings using embeddings.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with docstring indexing results.

### Function 10: `_perform_symbol_extraction(repo: Repository, output_dir: Path) -> dict`

- **Description**: Extracts symbol definitions (functions, classes, variables) from the codebase.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with symbol extraction results.

### Function 11: `_perform_symbol_usage_analysis(repo: Repository, symbols: list[str], output_dir: Path) -> dict`

- **Description**: Finds all usages of specified symbols across the repository.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `symbols` (list[str]): List of symbol names to analyze.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with symbol usage analysis results.

### Function 12: `_perform_text_search_context_extraction(repo: Repository, queries: list[str], output_dir: Path) -> dict`

- **Description**: Extracts context around text search matches for better understanding.
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `queries` (list[str]): List of text patterns to search for.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with context extraction results.

### Function 13: `_perform_chunking_examples(repo: Repository, output_dir: Path) -> dict`

- **Description**: Generates examples of code chunking strategies (by lines or symbols).
- **Parameters**:
    - `repo` (Repository): `cased/kit` Repository object.
    - `output_dir` (Path): Directory for output files.
- **Returns**: Dictionary with chunking examples.

## Data Models

### Model: `Repository` (from `cased/kit`)
- Core data structure representing a code repository.
- Provides methods for searching, analyzing, and extracting information from codebases.

### Model: Analysis Results
- Dictionary structure containing:
    - `success` (bool): Whether the analysis completed successfully.
    - `output_dir` (str): Directory where results were saved.
    - `results` (dict): Analysis-specific results and metadata.
    - `timestamp` (str): ISO format timestamp of analysis execution.

## Authentication & Authorization

- **API Keys**: Some features (semantic search, code summarization) require API keys configured in environment variables:
    - `OPENAI_API_KEY`: For OpenAI-based LLM features
    - `ANTHROPIC_API_KEY`: For Anthropic Claude-based features
    - `GOOGLE_API_KEY`: For Google Cloud-based features
- These are loaded via the `environment_setup` module from `.env` files.

## Rate Limiting

- LLM-based features (summarization, semantic search) are subject to rate limits imposed by the respective API providers (OpenAI, Anthropic, Google Cloud).
- The module does not implement client-side rate limiting; users should respect provider limits.

## Versioning

- This API follows the Codomyrmex project versioning strategy.
- API stability is maintained for public functions (`get_embedding_function`, `analyze_repository_path`, `run_full_analysis`, `print_once`).
- Internal functions (`_perform_*`) may change without notice.

## Integration Points

- **Consumes**:
    - `cased/kit` library for code analysis
    - `logging_monitoring` module for structured logging
    - `environment_setup` module for environment validation and API key loading
    - LLM APIs (OpenAI, Anthropic, Google Cloud) for advanced features

- **Provides**:
    - Analysis reports and structured data (JSON files, text files, DOT graphs)
    - MCP Tools: `search_text_pattern`, `find_symbol_occurrences`, `search_semantic_concept`
    - Programmatic API for code searches and analyses

## Usage Examples

See the module's `USAGE_EXAMPLES.md` and `MCP_TOOL_SPECIFICATION.md` for detailed usage examples and MCP tool integration.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
