# Codomyrmex Agents — src/codomyrmex/static_analysis

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing static code analysis capabilities for the Codomyrmex platform. This module performs automated code quality assessment, security scanning, and complexity analysis across multiple programming languages without executing the code.

The static_analysis module serves as the foundation for code quality assurance, enabling early detection of issues and enforcement of coding standards.

## Module Overview

### Key Capabilities
- **Code Quality Metrics**: Complexity analysis, maintainability scoring, and style checking
- **Security Scanning**: Vulnerability detection and security best practice validation
- **Language Support**: Multi-language analysis with language-specific rules
- **Automated Reporting**: Structured analysis results with actionable recommendations
- **Integration Ready**: Designed for CI/CD pipeline integration

### Key Features
- Comprehensive linting and code quality analysis
- Security vulnerability detection and reporting
- Cyclomatic complexity and maintainability metrics
- Multi-language support with extensible rule system
- Integration with logging and reporting systems

## Function Signatures

### Core Functions

```python
def analyze_file(
    file_path: str,
    analysis_types: list[AnalysisType] = None
) -> list[AnalysisResult]
```

Analyzes a single file for code quality, security, and maintainability issues.

**Parameters:**
- `file_path` (str): Path to the file to analyze
- `analysis_types` (list[AnalysisType], optional): Types of analysis to perform. If None, performs all available analyses

**Returns:** List of `AnalysisResult` objects containing issues found

```python
def analyze_project(
    project_root: str,
    target_paths: list[str] = None,
    analysis_types: list[AnalysisType] = None
) -> AnalysisSummary
```

Analyzes an entire project or specified paths within a project.

**Parameters:**
- `project_root` (str): Root directory of the project to analyze
- `target_paths` (list[str], optional): Specific paths within the project to analyze. If None, analyzes the entire project
- `analysis_types` (list[AnalysisType], optional): Types of analysis to perform. If None, performs all available analyses

**Returns:** `AnalysisSummary` object containing aggregated analysis results

```python
def get_available_tools() -> dict[str, bool]
```

Returns the availability status of all supported analysis tools.

**Returns:** Dictionary mapping tool names to boolean availability status

```python
def parse_pyrefly_output(output: str, project_root: str) -> list
```

Parses raw Pyrefly static analysis output into structured error information.

**Parameters:**
- `output` (str): Raw output from Pyrefly analysis
- `project_root` (str): Root directory of the project for path resolution

**Returns:** List of parsed error/issue dictionaries

```python
def run_pyrefly_analysis(target_paths: list[str], project_root: str) -> dict
```

Runs Pyrefly static type checker on specified paths.

**Parameters:**
- `target_paths` (list[str]): File or directory paths to analyze
- `project_root` (str): Root directory of the project for configuration and path resolution

**Returns:** Dictionary containing analysis results and metadata

```python
def analyze_codebase(*args, **kwargs) -> AnalysisSummary
```

Alias for `analyze_project()` for backward compatibility.

**Returns:** Same as `analyze_project()`

### Data Structures

```python
class AnalysisType(Enum):
    """Types of static analysis available."""
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    TESTING = "testing"

class SeverityLevel(Enum):
    """Severity levels for analysis results."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Language(Enum):
    """Supported programming languages for analysis."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
```

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `static_analyzer.py` – Main analysis engine and rule processing
- `pyrefly_runner.py` – Python-specific analysis runner

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for code analysis
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (linting tools, security scanners)
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Analysis Protocols

All static analysis within the Codomyrmex platform must:

1. **Non-Intrusive** - Analysis should not modify source code or affect runtime behavior
2. **Consistent Rules** - Apply uniform standards across all analyzed codebases
3. **Actionable Results** - Provide specific, fixable recommendations
4. **Performance Aware** - Optimize analysis for speed and resource efficiency
5. **Extensible Design** - Support addition of new rules and languages

### Module-Specific Guidelines

#### Analysis Execution
- Support analysis of individual files and entire codebases
- Provide configurable rule sets for different project types
- Generate structured reports suitable for CI/CD integration
- Handle analysis failures gracefully without stopping pipelines

#### Quality Metrics
- Calculate and report code complexity metrics
- Identify security vulnerabilities with severity levels
- Provide maintainability and readability assessments
- Support custom quality thresholds and policies

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

1. **CI/CD Integration** - Provide analysis results for automated quality gates
2. **Code Review Enhancement** - Supply analysis data to code review processes
3. **Security Coordination** - Work with security_audit for comprehensive assessment
4. **Reporting Integration** - Feed analysis results into reporting systems

### Quality Gates

Before analysis changes are accepted:

1. **Accuracy Verified** - Analysis correctly identifies code issues
2. **Performance Tested** - Analysis completes within reasonable time limits
3. **False Positive Management** - Minimize incorrect issue reporting
4. **Rule Consistency** - Analysis rules align with platform standards
5. **Integration Validated** - Results integrate properly with dependent systems

## Version History

- **v0.1.0** (December 2025) - Initial static analysis system with code quality and security scanning capabilities
