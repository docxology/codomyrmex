# Codomyrmex Agents — src/codomyrmex/pattern_matching

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Code analysis through AST parsing, pattern recognition, and embedding generation for semantic search and similarity. Provides multi-step pipeline (Parse -> Recognize -> Embed -> Analyze) with configurable patterns for code smells and other patterns. Utilizes the `cased/kit` toolkit for code analysis and pattern recognition.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `docs/` – Directory containing docs components
- `requirements.txt` – Project file
- `run_codomyrmex_analysis.py` – Main CLI and entry point for analysis
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Module Functions (`run_codomyrmex_analysis.py`)
- `get_embedding_function(model_name: str = "all-MiniLM-L6-v2") -> Optional[Callable]` – Get or create embedding function for semantic analysis (uses SentenceTransformer)
- `analyze_repository_path(repo_path: str, output_dir: str = "./output/codomyrmex_analysis") -> Repository` – Analyze a single repository path using cased/kit Repository object
- `run_full_analysis(repo_path: str, output_dir: str = "./output/codomyrmex_analysis") -> dict` – Run comprehensive analysis including all analysis types
- `print_once(message: str) -> None` – Print message only once (deduplication)

### Analysis Functions (`run_codomyrmex_analysis.py`)
- `_perform_repository_index(repo: Repository, output_dir: str) -> dict` – Perform basic repository indexing
- `_perform_dependency_analysis(repo: Repository, output_dir: str) -> dict` – Analyze dependencies
- `_perform_text_search(repo: Repository, query: str, output_dir: str) -> dict` – Perform text search
- `_perform_code_summarization(repo: Repository, output_dir: str) -> dict` – Summarize code
- `_perform_docstring_indexing(repo: Repository, output_dir: str) -> dict` – Index docstrings
- `_perform_symbol_extraction(repo: Repository, output_dir: str) -> dict` – Extract symbols (functions, classes, imports)
- `_perform_symbol_usage_analysis(repo: Repository, output_dir: str) -> dict` – Analyze symbol usage
- `_perform_text_search_context_extraction(repo: Repository, query: str, output_dir: str) -> dict` – Extract context for text search
- `_perform_chunking_examples(repo: Repository, output_dir: str) -> dict` – Perform code chunking examples

### Output Format
- All analysis functions output JSON files with structured analysis results

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation