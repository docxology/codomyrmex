# Pattern Matching Module (Leveraging `cased/kit`)

## Overview

This module focuses on identifying specific patterns and structures within the Codomyrmex codebase. It extensively utilizes the `cased/kit` toolkit, which provides powerful features for various types of pattern matching, code analysis, and search.

## Capabilities via `cased/kit`

`cased/kit` enables diverse pattern matching and analysis, including:

1.  **Text and Regular Expression Search:**
    -   The `Repository.search_text()` method (or the `CodeSearcher` class) allows for fast and efficient searching of literal strings or regular expressions across files.
    -   Useful for finding keywords, API usage, log messages, or known code anti-patterns.
    -   Demonstrated in `kit_text_search_example.py` and used by the `search_text_pattern` MCP tool.

2.  **Symbol Usage Search & Analysis:**
    -   The `Repository.find_symbol_usages()` method and symbol extraction capabilities help locate where specific symbols (functions, classes, variables) are defined and referenced.
    -   This structural pattern matching is key for understanding component connections, identifying all instances of a function call, and performing impact analysis.
    -   Demonstrated in `kit_symbol_search_example.py` and used by the `find_symbol_occurrences` MCP tool.

3.  **Semantic Search (Advanced):**
    -   For conceptual pattern matching (e.g., "find all places that handle user authentication"), `kit`'s semantic search (`Repository.search_semantic()` or `SummarySearcher`) can be employed. This requires setting up vector embeddings for the codebase.
    -   Allows finding code that matches a *concept* or *description*, going beyond literal text or symbol names.
    -   Used by the `search_semantic_concept` MCP tool.

4.  **Dependency Analysis & Code Summarization:**
    -   The `run_codomyrmex_analysis.py` script also utilizes `cased/kit` for Python dependency analysis and LLM-based code summarization, which can be seen as forms of structural and semantic pattern recognition respectively.

## Key Components

- **`run_codomyrmex_analysis.py`**: The primary script in this module. It orchestrates various analyses using `cased/kit` across the repository (or specified sub-paths), generating reports on dependencies, text patterns, code summaries, and docstring indexes. It serves as a comprehensive example of leveraging `cased/kit`.
- **Example Scripts (`kit_text_search_example.py`, `kit_symbol_search_example.py`)**: Standalone examples demonstrating specific `cased/kit` search functionalities.
- **`cased/kit` Library Integration**: The core of this module involves wrappers and utility functions that interact directly with the `cased/kit` API.
- **MCP Tool Implementations**: Logic that implements the `search_text_pattern`, `find_symbol_occurrences`, and `search_semantic_concept` tools, making these capabilities available via the Model Context Protocol.
- **Configuration for `cased/kit`**: Manages settings for `cased/kit`, including repository paths, indexing options, and LLM configurations (sourced via `.env` through the `environment_setup` module's utilities).

## Integration Points

This module interacts with several other parts of the Codomyrmex system and external services:

- **Provides:**
    - Analysis reports and structured data (e.g., JSON files, text files, DOT graphs from `run_codomyrmex_analysis.py`). These are typically saved to the `output/codomyrmex_analysis/` directory (this path is configurable within the script).
    - MCP Tools: Exposes `search_text_pattern`, `find_symbol_occurrences`, and `search_semantic_concept` for programmatic pattern matching (see `MCP_TOOL_SPECIFICATION.md`).
    - A programmatic API (via its Python scripts and `cased/kit` direct usage) for performing various code searches and analyses.

- **Consumes:**
    - **`cased/kit` library**: This is the fundamental dependency, used for all analysis tasks.
    - **`logging_monitoring` module**: Utilizes `setup_logging()` and `get_logger()` for structured logging, especially in `run_codomyrmex_analysis.py`.
    - **`environment_setup` module (specifically `env_checker.py`)**: `run_codomyrmex_analysis.py` calls `ensure_core_deps_installed()` and `check_and_setup_env_vars()` to validate the environment and `.env` file (crucial for API keys like `OPENAI_API_KEY` needed by `cased/kit`'s LLM-dependent features).
    - **`model_context_protocol` module**: Adheres to MCP standards for defining its exposed tools.
    - **LLM APIs (via `cased/kit`)**: For semantic search and summarization features, it indirectly consumes services from OpenAI, Anthropic, or Google Cloud, configured via API keys loaded from the `.env` file.
    - **Source Code**: The Codomyrmex project's source code itself is the primary input for analysis.

- Refer to the [API Specification](API_SPECIFICATION.md) (placeholder for any direct API this module might formalize beyond script execution) and the [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) for detailed programmatic interfaces.

## Getting Started

To utilize the Pattern Matching module:

1.  **Ensure Environment Setup**: Verify that your Codomyrmex development environment is fully set up as per the main project `README.md` and/or `environment_setup/README.md`. This includes installation of `cased/kit` from the root `requirements.txt` and configuration of any necessary API keys in a `.env` file at the project root (e.g., `OPENAI_API_KEY` for semantic search or summarization).
2.  **Run the Main Analysis Script (Optional Comprehensive Analysis)**:
    Execute `python pattern_matching/run_codomyrmex_analysis.py` from the project root. This script performs a wide range of analyses and saves outputs to `output/codomyrmex_analysis/`. Review the script's `ANALYSIS_CONFIG` dictionary for options to toggle different analysis stages.
    ```bash
    # From the codomyrmex project root
    python pattern_matching/run_codomyrmex_analysis.py
    ```
3.  **Explore Example Scripts**: To understand specific `cased/kit` functionalities:
    ```bash
    # From the codomyrmex project root
    python pattern_matching/kit_text_search_example.py
    python pattern_matching/kit_symbol_search_example.py
    ```
    These scripts might require minor adjustments (e.g., repository path if not running from root) or can be used as templates.
4.  **Utilize MCP Tools**: For programmatic interaction (e.g., from an AI agent or another module), use the defined MCP tools: `search_text_pattern`, `find_symbol_occurrences`, and `search_semantic_concept`. Refer to this module's `MCP_TOOL_SPECIFICATION.md` for their detailed schemas and usage.

### Prerequisites

- **Codomyrmex Environment**: Fully set up, including Python and `pip`.
- **`cased/kit` Installation**: Installed as part of the root `requirements.txt`.
- **API Keys (for advanced features)**: If using semantic search or LLM-based summarization via `run_codomyrmex_analysis.py` or the `search_semantic_concept` MCP tool, ensure relevant API keys (e.g., `OPENAI_API_KEY`) are present in the project's root `.env` file.
- **Git**: `cased/kit` often interacts with Git repositories.

### Installation

This module is part of the Codomyrmex project. Cloning the repository and setting up the main Python environment (which installs `cased/kit` from the root `requirements.txt`) is sufficient.
If this module had specific Python dependencies not in the root `requirements.txt`, they would be listed in `pattern_matching/requirements.txt` and installed via:
```bash
pip install -r pattern_matching/requirements.txt
```
(Currently, it relies on the root `requirements.txt` for `cased/kit`).

### Configuration

- **`run_codomyrmex_analysis.py`**: Configured internally via the `REPO_ROOT_PATH`, `BASE_OUTPUT_DIR_NAME`, `MODULE_DIRS`, and `ANALYSIS_CONFIG` variables within the script itself. Users might modify these directly in the script for custom runs.
- **`.env` File**: For API keys used by `cased/kit` (e.g., `OPENAI_API_KEY`). See `environment_setup/README.md`.
- **`cased/kit` Indexing**: Some `cased/kit` features (like semantic search or rapid symbol lookup) may rely on pre-built indexes. The `run_codomyrmex_analysis.py` script includes steps for some of these (e.g., docstring indexing).

## Development

Contributions could involve adding new analysis types to `run_codomyrmex_analysis.py`, refining existing ones, creating more example scripts, or enhancing MCP tools.

### Code Structure

- `README.md`: This file.
- `run_codomyrmex_analysis.py`: Main orchestration script for various `cased/kit` analyses.
- `kit_text_search_example.py`, `kit_symbol_search_example.py`: Example usage scripts.
- `MCP_TOOL_SPECIFICATION.md`: Defines MCP tools for this module.
- `API_SPECIFICATION.md`: Placeholder for any formal Python API this module might expose.
- `requirements.txt`: For module-specific Python dependencies (currently minimal, relies on root).
- `docs/`: Detailed documentation (technical overview, tutorials).
- `tests/`: Unit and integration tests.

### Building & Testing

- **Building**: No specific build step for this Python-based module.
- **Testing**:
    1.  **Install Dependencies**: Ensure project root and any module-specific dependencies are installed. For testing, `pytest` and mocking libraries would be needed.
        ```bash
        pip install -r requirements.txt # Project root
        pip install pytest pytest-mock # Example test dependencies
        ```
    2.  **Run Tests**: Using `pytest` from the project root.
        ```bash
        pytest pattern_matching/tests/
        ```
    - **Unit Tests (`tests/unit`)**: Test helper functions within `run_codomyrmex_analysis.py` or any utility scripts, mocking calls to `cased/kit` methods.
    - **Integration Tests (`tests/integration`)**: Test the MCP tool implementations by invoking them with sample inputs and verifying outputs. Test the `run_codomyrmex_analysis.py` script with a small, controlled (mocked or temporary) repository structure to ensure it generates expected reports without relying on external LLM calls in automated tests (or using specifically configured test LLM endpoints if available).
    - Refer to `pattern_matching/tests/README.md` for more specific testing instructions.

## Further Information

- [API Specification](API_SPECIFICATION.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md)
- [Usage Examples](USAGE_EXAMPLES.md) (Covers `run_codomyrmex_analysis.py` and example scripts)
- [Detailed Documentation](./docs/index.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md) 