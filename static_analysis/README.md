# Static Analysis

## Overview

The Static Analysis module provides tools and integrations for analyzing source code without executing it. Its core purpose is to enhance code quality, identify potential bugs, enforce coding standards, and detect security vulnerabilities early in the development lifecycle. This module may incorporate linters, style checkers, complexity analyzers, and other static analysis tools relevant to the languages and frameworks used within the Codomyrmex project.

## Key Components

- **Linter Integrations**: Support for or wrappers around common linters (e.g., Pylint, Flake8 for Python; ESLint for JavaScript) to identify code errors, style issues, and potential bugs.
- **Type Checker Integrations**: Support for advanced type checkers like Pyrefly to enhance type safety and code reliability.
- **Style Checker Integrations**: Tools for enforcing consistent code style (e.g., Black, Prettier).
- **Security Scanning Tools**: Integration with static application security testing (SAST) tools (e.g., Bandit for Python) to detect common security vulnerabilities in code.
- **Code Complexity Analyzers**: Tools to measure cyclomatic complexity, cognitive complexity, or other metrics to identify overly complex code sections.
- **Configuration Management**: Centralized or per-language configurations for the various static analysis tools used.
- **Reporting Utilities**: Scripts or mechanisms to aggregate and report findings from different analysis tools.

## Integration Points

This module plays a key role in maintaining code quality and security:

- **Provides:**
    - **Analysis Reports**: Outputs from linters, style checkers, and security scanners, indicating potential issues, style violations, and vulnerabilities.
    - **Pre-commit Hooks**: May provide configurations for pre-commit hooks that run static analysis checks automatically before code is committed.
    - **CI/CD Integration Points**: Scripts or configurations to integrate static analysis into Continuous Integration pipelines, enabling automated checks on every change.
    - **Code Quality Metrics**: Data on code complexity, test coverage (if integrated), or other quality indicators.

- **Consumes:**
    - **Source Code**: Analyzes source code from all modules within the Codomyrmex project written in supported languages (e.g., Python, JavaScript).
    - **Configuration Files**: Reads configuration files for various static analysis tools (e.g., `.pylintrc`, `pyproject.toml` for Black/Flake8, `.eslintrc.js`) to apply project-specific rules and standards.
    - **`build_synthesis` module**: May be triggered by the build module as a quality gate before or during the build process.
    - **`logging_monitoring` module**: For logging analysis activities, summaries of findings, and any errors encountered during analysis.

- Refer to the [API Specification](API_SPECIFICATION.md) and [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) for detailed programmatic interfaces.)

## Getting Started

The Static Analysis module is primarily designed to be used programmatically, often as part of automated CI/CD pipelines or development workflows. It exposes its core functionality through the `run_static_analysis` tool, as defined in the [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md).

This tool allows you to analyze specified source files or directories using a configurable set of static analysis utilities.

**Conceptual Usage (via MCP):**
To analyze a module, you would typically invoke the `run_static_analysis` tool with parameters specifying the target paths and desired analysis tools. For example:
```json
{
  "tool_name": "run_static_analysis",
  "arguments": {
    "target_paths": ["src/my_module/"],
    "tools": ["pylint", "bandit", "pyrefly"],
    "language": "python"
  }
}
```
Refer to [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) and the [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) for more detailed examples.

### Prerequisites

- **Python**: This module and its primary tools are Python-based. Ensure Python (version as specified in the root project, e.g., 3.9+) is installed.
- **Static Analysis Tools**: The module integrates several Python-based static analysis tools. Key tools specified in `requirements.txt` include:
    - Pylint (Linter)
    - Flake8 (Linter)
    - Bandit (Security Scanner)
    - Radon (Complexity Metrics)
    - Lizard (Cyclomatic Complexity)
    - Pyrefly (Type Checker)
- Project-wide dependencies as listed in the root `requirements.txt`.

### Installation

1.  **Install Project Dependencies**: Ensure all general project dependencies are installed from the root directory:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Install Module-Specific Dependencies**: Install the static analysis tools required by this module:
    ```bash
    pip install -r static_analysis/requirements.txt
    ```

### Configuration

Configuration for the Static Analysis module primarily involves:

1.  **`run_static_analysis` Tool Parameters**: As detailed in the [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md), you can configure:
    - `target_paths`: The specific files or directories to analyze.
    - `tools`: An array of tool names (e.g., "pylint", "flake8", "pyrefly") to execute. If omitted, a default set of primary tools may run.
    - `language`: To help select appropriate tools or configurations (e.g., "python").
    - `config_file`: Path to a custom, overarching configuration file (if supported by the runner implementation).
    - `options`: Tool-specific options.

2.  **Individual Tool Configurations**: Many of the integrated static analysis tools (like Pylint, Flake8, Bandit, Pyrefly) support their own configuration files (e.g., `.pylintrc`, `pyproject.toml` for Black/Flake8/Pyrefly, `.bandit`, `pyrefly.toml`). These files should be placed in appropriate locations within the project (often the root or module directory) for the tools to discover them. Refer to the documentation of each specific tool for its configuration options and file formats.

## Development

This section provides information for developers contributing to the Static Analysis module.

### Code Structure

The module is structured to integrate various static analysis tools under a common interface, primarily exposed via the `run_static_analysis` MCP tool.
- Core logic for invoking and aggregating results from different tools would reside in Python scripts within this module.
- `MCP_TOOL_SPECIFICATION.md`: Defines the contract for the `run_static_analysis` tool.
- `requirements.txt`: Lists specific linters and analysis tools.
- `docs/`: Contains detailed documentation, including the [Technical Overview](./docs/technical_overview.md) which provides more insight into the architecture.
- `tests/`: Contains unit and integration tests.

### Building & Testing

Testing is crucial for ensuring the reliability of the static analysis tools and their integration.
- **Test Organization**: Tests are organized into `unit/` and `integration/` subdirectories within the `static_analysis/tests/` directory. Fixtures or test data might be located in `static_analysis/tests/fixtures/` or `static_analysis/tests/data/`.
- **Running Tests**:
    - Refer to the [tests/README.md](./tests/README.md) for comprehensive testing instructions.
    - To run unit tests:
      ```bash
      pytest static_analysis/tests/unit
      ```
    - To run integration tests (which might involve analyzing sample code):
      ```bash
      pytest static_analysis/tests/integration
      ```
    (Ensure `pytest` is installed and configured for the project.)

## Further Information

- [API Specification](API_SPECIFICATION.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) (If this module exposes tools via MCP)
- [Usage Examples](USAGE_EXAMPLES.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md) 