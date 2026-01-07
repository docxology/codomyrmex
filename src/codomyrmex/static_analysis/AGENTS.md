# Codomyrmex Agents — src/codomyrmex/static_analysis

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
Automated code quality assessment without execution. Orchestrates parsers and analyzers to detect syntax errors, security vulnerabilities, complexity issues, and code quality problems. Provides language-agnostic architecture allowing plugging in analyzers for any language with graceful failure handling.

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
- `pyrefly_runner.py` – Pyrefly analysis runner
- `requirements.txt` – Project file
- `static_analyzer.py` – Main static analyzer implementation
- `tests/` – Directory containing tests components

## Key Classes and Functions

### StaticAnalyzer (`static_analyzer.py`)
- `StaticAnalyzer(project_root: str = None)` – Main static analyzer class
- `analyze_file(file_path: str, analysis_types: list[AnalysisType] = None) -> list[AnalysisResult]` – Analyze a single file for various issues
- `analyze_project(project_path: str, analysis_types: list[AnalysisType] = None) -> AnalysisSummary` – Analyze an entire project
- `_check_tools_availability() -> dict[str, bool]` – Check which analysis tools are available (pylint, flake8, mypy, bandit, black, isort, pytest, coverage, radon, vulture, safety, semgrep, pyrefly)

### AnalysisResult (`static_analyzer.py`)
- `AnalysisResult` (dataclass) – Individual analysis result:
  - `file_path: str` – File path
  - `line_number: Optional[int]` – Line number
  - `column_number: Optional[int]` – Column number
  - `message: str` – Analysis message
  - `severity: SeverityLevel` – Severity level
  - `analysis_type: AnalysisType` – Type of analysis
  - `rule_id: Optional[str]` – Rule identifier
  - `suggestion: Optional[str]` – Suggestion for fix

### AnalysisSummary (`static_analyzer.py`)
- `AnalysisSummary` (dataclass) – Summary of analysis results:
  - `total_files: int` – Total files analyzed
  - `total_issues: int` – Total issues found
  - `issues_by_severity: dict[SeverityLevel, int]` – Issues grouped by severity
  - `issues_by_type: dict[AnalysisType, int]` – Issues grouped by type
  - `metrics: CodeMetrics` – Code quality metrics

### CodeMetrics (`static_analyzer.py`)
- `CodeMetrics` (dataclass) – Code quality metrics:
  - `cyclomatic_complexity: Optional[float]` – Cyclomatic complexity
  - `maintainability_index: Optional[float]` – Maintainability index
  - `lines_of_code: Optional[int]` – Lines of code
  - `test_coverage: Optional[float]` – Test coverage percentage
  - `documentation_coverage: Optional[float]` – Documentation coverage percentage

### AnalysisType (`static_analyzer.py`)
- `AnalysisType` (Enum) – Types of static analysis: QUALITY, SECURITY, PERFORMANCE, MAINTAINABILITY, COMPLEXITY, STYLE, DOCUMENTATION, TESTING

### SeverityLevel (`static_analyzer.py`)
- `SeverityLevel` (Enum) – Severity levels: INFO, WARNING, ERROR, CRITICAL

### Module Functions (`__init__.py`)
- `analyze_file(file_path: str, analysis_types: list[AnalysisType] = None) -> list[AnalysisResult]` – Analyze a single file
- `analyze_project(project_path: str, analysis_types: list[AnalysisType] = None) -> AnalysisSummary` – Analyze entire project
- `get_available_tools() -> list[str]` – Get list of available analysis tools
- `run_pyrefly_analysis(target_paths: list[str], **kwargs) -> dict` – Run Pyrefly static analysis
- `parse_pyrefly_output(output: str) -> list[AnalysisResult]` – Parse pyrefly analysis output
- `analyze_codebase(*args, **kwargs)` – Alias for analyze_project (backward compatibility)

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation