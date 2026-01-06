# Codomyrmex Agents — src/codomyrmex/code_review

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Code Review Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing automated code review and quality assessment capabilities for the Codomyrmex platform. This module performs intelligent analysis of code changes, provides actionable feedback, and supports both automated and human-in-the-loop code review workflows.

The code_review module serves as the quality assurance backbone, enabling consistent and intelligent code review processes throughout the platform.

## Module Overview

### Key Capabilities
- **Automated Code Analysis**: Intelligent review of code changes and pull requests
- **Quality Metrics**: Code quality scoring and improvement recommendations
- **Style Consistency**: Automated style guide enforcement and suggestions
- **Security Review**: Integration with security scanning for vulnerability detection
- **Performance Analysis**: Identification of performance bottlenecks and optimization opportunities
- **Documentation Review**: Assessment of code documentation completeness

### Key Features
- Multi-language code review support
- Configurable review rules and policies
- Integration with version control systems
- Automated feedback generation
- Review metrics and trend analysis
- Custom rule engine for organization-specific standards

## Function Signatures

### Core Analysis Functions

```python
def analyze_file(file_path: str, analysis_types: list[str] = None) -> list[AnalysisResult]
```

Analyze a single file for code quality issues.

**Parameters:**
- `file_path` (str): Path to the file to analyze
- `analysis_types` (list[str]): Types of analysis to perform. If None, performs all available analyses

**Returns:** `list[AnalysisResult]` - List of analysis results and findings

```python
def analyze_project(
    project_root: str,
    target_paths: list[str] = None,
    analysis_types: list[str] = None,
) -> AnalysisSummary
```

Analyze an entire project for code quality issues.

**Parameters:**
- `project_root` (str): Root directory of the project to analyze
- `target_paths` (list[str]): Specific paths to analyze. If None, analyzes entire project
- `analysis_types` (list[str]): Types of analysis to perform. If None, performs all available analyses

**Returns:** `AnalysisSummary` - Summary of analysis results across the project

```python
def check_quality_gates(project_root: str, thresholds: dict[str, int] = None) -> QualityGateResult
```

Check if project meets quality standards and thresholds.

**Parameters:**
- `project_root` (str): Root directory of the project to check
- `thresholds` (dict[str, int]): Quality thresholds to check against. If None, uses defaults

**Returns:** `QualityGateResult` - Quality gate check results with pass/fail status

```python
def generate_report(
    project_root: str,
    report_format: str = "html",
    output_path: str = None,
) -> str
```

Generate a code review report.

**Parameters:**
- `project_root` (str): Root directory of the analyzed project
- `report_format` (str): Report format ("html", "json", "text"). Defaults to "html"
- `output_path` (str): Path to save report. If None, returns report content as string

**Returns:** `str` - Report content or path to saved report file

## Data Structures

### AnalysisResult
```python
class AnalysisResult:
    file_path: str
    line_number: int
    column: int
    severity: SeverityLevel
    category: str
    message: str
    rule_id: str
    suggestion: str
    context: dict[str, Any]

    def to_dict(self) -> dict[str, Any]
    def __str__(self) -> str
```

Individual code analysis finding with location, severity, and remediation information.

### AnalysisSummary
```python
class AnalysisSummary:
    project_root: str
    total_files: int
    analyzed_files: int
    total_issues: int
    issues_by_severity: dict[SeverityLevel, int]
    issues_by_category: dict[str, int]
    analysis_time: float
    results: list[AnalysisResult]

    def get_files_with_issues(self) -> list[str]
    def get_top_issues(self, limit: int = 10) -> list[AnalysisResult]
    def to_dict(self) -> dict[str, Any]
```

Summary of analysis results across multiple files with statistics and aggregations.

### QualityGateResult
```python
class QualityGateResult:
    passed: bool
    failed_checks: list[str]
    metrics: dict[str, int]
    thresholds: dict[str, int]
    details: dict[str, Any]

    def get_failed_metrics(self) -> dict[str, int]
    def to_dict(self) -> dict[str, Any]
```

Results of quality gate checks with pass/fail status and detailed metrics.

### CodeReviewer
```python
class CodeReviewer:
    def __init__(self, project_root: str = None)

    def analyze_file(self, file_path: str, analysis_types: list[str] = None) -> list[AnalysisResult]
    def analyze_project(self, target_paths: list[str] = None, analysis_types: list[str] = None) -> AnalysisSummary
    def check_quality_gates(self, thresholds: dict[str, int] = None) -> QualityGateResult
    def generate_report(self, format: str = "html", output_path: str = None) -> str
    def get_supported_analyses(self) -> list[str]
    def configure_analysis(self, analysis_type: str, config: dict[str, Any]) -> None
```

Main code review engine providing analysis capabilities.

### PyscnAnalyzer
```python
class PyscnAnalyzer:
    def __init__(self, config: dict[str, Any] = None)

    def analyze_code(self, code: str, file_path: str = None) -> list[AnalysisResult]
    def analyze_file(self, file_path: str) -> list[AnalysisResult]
    def get_supported_languages(self) -> list[str]
    def configure_rules(self, rules_config: dict[str, Any]) -> None
    def get_available_rules(self) -> list[str]
```

Advanced code analysis using pyscn integration for multi-language support.

### QualityDashboard
```python
class QualityDashboard:
    def __init__(self, analysis_summary: AnalysisSummary)

    def generate_dashboard(self, output_format: str = "html") -> str
    def get_quality_score(self) -> float
    def get_trend_data(self, historical_data: list[AnalysisSummary]) -> dict[str, Any]
    def export_metrics(self, format: str = "json") -> str
    def generate_recommendations(self) -> list[str]
```

Interactive quality dashboard for visualizing code review results and trends.

### CodeMetrics
```python
class CodeMetrics:
    lines_of_code: int
    cyclomatic_complexity: float
    maintainability_index: float
    halstead_metrics: dict[str, float]
    duplication_percentage: float
    test_coverage: float

    def calculate_overall_score(self) -> float
    def get_improvement_suggestions(self) -> list[str]
    def to_dict(self) -> dict[str, Any]
```

Comprehensive code metrics for quality assessment.

## Analysis Types

### AnalysisType Enum
```python
class AnalysisType(Enum):
    STYLE = "style"
    COMPLEXITY = "complexity"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    DUPLICATION = "duplication"
    DEPENDENCIES = "dependencies"
    ARCHITECTURE = "architecture"
```

Types of code analysis that can be performed.

### SeverityLevel Enum
```python
class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

Severity levels for analysis findings.

### Language Enum
```python
class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
```

Supported programming languages for analysis.

## Specialized Finding Types

### DeadCodeFinding
```python
class DeadCodeFinding:
    function_name: str
    file_path: str
    line_number: int
    reason: str
    confidence: float

    def to_dict(self) -> dict[str, Any]
    def suggest_removal(self) -> str
```

Finding for dead or unreachable code.

### ArchitectureViolation
```python
class ArchitectureViolation:
    violation_type: str
    component: str
    dependency: str
    severity: SeverityLevel
    description: str
    suggestion: str

    def to_dict(self) -> dict[str, Any]
    def get_fix_command(self) -> str
```

Finding for architectural rule violations.

### ComplexityReductionSuggestion
```python
class ComplexityReductionSuggestion:
    function_name: str
    current_complexity: int
    target_complexity: int
    suggestions: list[str]
    estimated_effort: str

    def to_dict(self) -> dict[str, Any]
    def get_refactoring_plan(self) -> list[str]
```

Suggestions for reducing code complexity.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `code_review.py` – Main code review engine and analysis
- `demo_review.py` – Review demonstration and examples

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for code review
- `CHANGELOG.md` – Version history and updates

### Testing
- `test_simple.py` – Simple test examples
- `tests/` – Comprehensive test suite

### Supporting Files
- `requirements.txt` – Module dependencies (code analysis tools, AI libraries)
- `docs/` – Additional documentation

## Operating Contracts

### Universal Code Review Protocols

All code review activities within the Codomyrmex platform must:

1. **Consistent Standards** - Apply uniform review criteria across all codebases
2. **Actionable Feedback** - Provide specific, fixable recommendations
3. **Educational Focus** - Help developers improve code quality over time
4. **Performance Aware** - Review processes don't significantly impact development velocity
5. **Security Integration** - Include security considerations in review feedback

### Module-Specific Guidelines

#### Review Automation
- Support both pre-commit and continuous integration review workflows
- Provide configurable review thresholds and policies
- Include review result caching to avoid redundant analysis
- Support incremental review of code changes

#### Quality Assessment
- Implement multi-dimensional quality scoring (style, performance, security, etc.)
- Provide severity levels for different types of issues
- Include automated fix suggestions where possible
- Track review quality trends over time

#### Integration Support
- Integrate with popular version control platforms (GitHub, GitLab, etc.)
- Support webhook-based automated reviews
- Provide API endpoints for custom integrations
- Include review result export capabilities

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation