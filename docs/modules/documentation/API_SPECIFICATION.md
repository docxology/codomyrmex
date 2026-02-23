# Documentation - API Specification

## Introduction

This document outlines the specification for the programmatic APIs provided by the `documentation` module. The module manages Docusaurus-based documentation websites, aggregates module documentation, validates version consistency, and assesses documentation quality.

The primary interface for interacting with this module's functionalities is through:
1. The `documentation_website.py` command-line script.
2. MCP (Model Context Protocol) tools like `trigger_documentation_build` and `check_documentation_environment`, detailed in `MCP_TOOL_SPECIFICATION.md`.
3. Direct Python function imports from `codomyrmex.documentation`.

## Endpoints / Functions / Interfaces

### Function: `check_doc_environment() -> bool`

- **Description**: Check for Node.js and npm/yarn availability in the system PATH. Logs findings and returns whether the basic documentation environment is ready.
- **Parameters**: None.
- **Return Value**: `True` if Node.js and at least one package manager (npm or yarn) are available, `False` otherwise.
- **Errors**: Does not raise exceptions; logs errors for missing dependencies.

### Function: `run_command_stream_output(command_parts: list[str], cwd: str) -> bool`

- **Description**: Helper to run a shell command and stream its stdout/stderr output to the logger in real time.
- **Parameters**:
    - `command_parts` (list[str]): List of command arguments.
    - `cwd` (str): Working directory for the command.
- **Return Value**: `True` if the command executed successfully (exit code 0), `False` otherwise.
- **Errors**: Returns `False` on `FileNotFoundError` or other exceptions; does not raise.

### Function: `install_dependencies(package_manager: str = "npm") -> bool`

- **Description**: Install Docusaurus dependencies using the specified package manager.
- **Parameters**:
    - `package_manager` (str, optional): Package manager to use (`"npm"` or `"yarn"`). Falls back to npm if yarn is specified but not found. Default: `"npm"`.
- **Return Value**: `True` if installation succeeded, `False` otherwise.
- **Errors**: Returns `False` if neither npm nor yarn is found.

### Function: `start_dev_server(package_manager: str = "npm") -> bool`

- **Description**: Start the Docusaurus development server with hot-reloading. This is a blocking call that runs until interrupted (Ctrl+C).
- **Parameters**:
    - `package_manager` (str, optional): Package manager to use (`"npm"` or `"yarn"`). Default: `"npm"`.
- **Return Value**: `True` when the server process finishes or is interrupted, `False` on error.
- **Errors**: Returns `False` if neither npm nor yarn is found or if the server fails to start.

### Function: `build_static_site(package_manager: str = "npm") -> bool`

- **Description**: Build the static Docusaurus site for deployment. Output is placed in the `build/` directory within the documentation module root.
- **Parameters**:
    - `package_manager` (str, optional): Package manager to use (`"npm"` or `"yarn"`). Default: `"npm"`.
- **Return Value**: `True` if the build completed successfully, `False` otherwise.
- **Errors**: Returns `False` on build failures.

### Function: `serve_static_site(package_manager: str = "npm") -> bool`

- **Description**: Serve the previously built static Docusaurus site. This is a blocking call. Requires the `build/` directory to exist and contain built files.
- **Parameters**:
    - `package_manager` (str, optional): Package manager to use (`"npm"` or `"yarn"`). Default: `"npm"`.
- **Return Value**: `True` when the server process finishes or is interrupted, `False` on error.
- **Errors**: Returns `False` if the build directory does not exist or is empty.

### Function: `print_assessment_checklist() -> None`

- **Description**: Print a checklist to stdout for manually assessing the documentation website. Covers navigation, content rendering, links, code blocks, and console errors.
- **Parameters**: None.
- **Return Value**: None. Prints to stdout as a side effect.

### Function: `aggregate_docs(source_root: str = None, dest_root: str = None) -> None`

- **Description**: Aggregate module documentation into the Docusaurus `docs/modules/` folder. Copies canonical documentation files (`README.md`, `API_SPECIFICATION.md`, `MCP_TOOL_SPECIFICATION.md`, `USAGE_EXAMPLES.md`, `CHANGELOG.md`, `SECURITY.md`) and the `docs/` subfolder from each `src/codomyrmex/<module>/` directory.
- **Parameters**:
    - `source_root` (str, optional): Root directory containing module source directories. Default: `{project_root}/src/codomyrmex`.
    - `dest_root` (str, optional): Destination directory for aggregated docs. Default: `{documentation_module}/docs/modules`.
- **Return Value**: None. Logs progress and results.
- **Errors**: Logs errors for individual file copy failures but continues processing.

### Function: `validate_doc_versions() -> tuple[bool, list[str], list[str]]`

- **Description**: Validate version consistency between source and aggregated documentation files. Compares CHANGELOG.md content and checks file modification timestamps.
- **Parameters**: None.
- **Return Value**: Tuple of `(is_valid, errors, warnings)` where:
    - `is_valid` (bool): `True` if no validation errors were found.
    - `errors` (list[str]): List of error messages for content mismatches.
    - `warnings` (list[str]): List of warning messages for stale aggregated docs.
- **Errors**: Does not raise; returns errors in the result tuple.

### Function: `assess_site() -> None`

- **Description**: Open the documentation website URL in the default web browser and print the assessment checklist to stdout. Requires a running documentation server.
- **Parameters**: None.
- **Return Value**: None. Opens browser and prints checklist as side effects.
- **Errors**: Logs warning if browser cannot be opened automatically.

### Function: `generate_quality_report(file_path: Path) -> dict[str, float]`

- **Description**: Generate a quality assessment report for a single documentation file. Analyzes completeness, consistency, technical accuracy, readability, and structure.
- **Parameters**:
    - `file_path` (Path): Path to the documentation file to analyze.
- **Return Value**: Dictionary of quality metric scores.

## Classes

### `DocumentationQualityAnalyzer`

Analyzes documentation quality metrics.

```python
class DocumentationQualityAnalyzer:
    def __init__(self): ...
    def analyze_file(self, file_path: Path) -> dict[str, float]: ...
```

**`analyze_file(file_path: Path) -> dict[str, float]`**: Analyze a single documentation file and return quality scores:
```python
{
    "completeness": float,
    "consistency": float,
    "technical_accuracy": float,
    "readability": float,
    "structure": float,
    "overall_score": float
}
```

### `DocumentationConsistencyChecker`

Checks documentation for consistency issues including naming conventions, formatting standards, and content alignment.

```python
class DocumentationConsistencyChecker:
    def __init__(self, config: dict[str, Any] | None = None): ...
```

Uses `ConsistencyIssue` and `ConsistencyReport` dataclasses for results.

## Data Structures

### DocumentationBuildConfig
Configuration for documentation build process:
```python
{
    "source_dir": str,
    "output_dir": str,
    "package_manager": str,
    "build_options": {
        "minify": bool,
        "optimize_images": bool,
        "generate_sitemap": bool
    },
    "metadata": {
        "version": str,
        "last_updated": timestamp,
        "author": str
    }
}
```

### ConsistencyIssue (dataclass)
```python
@dataclass
class ConsistencyIssue:
    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str = "warning"
    suggestion: str | None = None
```

### ConsistencyReport (dataclass)
```python
@dataclass
class ConsistencyReport:
    total_files: int
    files_checked: int
    issues: list[ConsistencyIssue] = field(default_factory=list)
    passed: bool = True
```

## Security Considerations

All documentation functions operate locally and do not expose network interfaces. Security considerations include:

- **Input Validation**: All file paths and parameters are validated before processing
- **Safe Execution**: Documentation commands are executed in controlled environments
- **Access Control**: File system access is limited to documentation directories
- **Output Sanitization**: Generated content is validated for security issues

## Performance Characteristics

- **Local Processing**: All operations performed locally with no external API calls
- **Resource Efficient**: Minimal memory and CPU usage for documentation operations
- **Streaming Output**: Real-time output streaming for long-running operations via `run_command_stream_output`

## Integration Patterns

### With Build Synthesis
```python
from codomyrmex.documentation import build_static_site

# Build documentation as part of CI/CD
build_result = build_static_site(package_manager="npm")
```

### Documentation Aggregation
```python
from codomyrmex.documentation import aggregate_docs, validate_doc_versions

# Aggregate documentation from all modules
aggregate_docs()

# Validate version consistency
is_valid, errors, warnings = validate_doc_versions()
```

### Quality Assessment
```python
from codomyrmex.documentation import DocumentationQualityAnalyzer

analyzer = DocumentationQualityAnalyzer()
report = analyzer.analyze_file(Path("docs/README.md"))
print(f"Overall score: {report['overall_score']}")
```
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
