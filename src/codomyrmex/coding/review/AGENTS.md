# Codomyrmex Agents — src/codomyrmex/coding/review

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides comprehensive code review and static analysis capabilities including pyscn integration for advanced code quality assessment, complexity analysis, dead code detection, code duplication detection, and quality dashboards.

## Active Components

- `reviewer.py` - Main code review functionality with `CodeReviewer` class
- `analyzer.py` - Pyscn integration with `PyscnAnalyzer` class
- `models.py` - Data models for analysis results including `QualityDashboard`
- `demo_review.py` - Demonstration and testing utilities
- `__init__.py` - Module exports

## Key Classes and Functions

### reviewer.py
- **`CodeReviewer`** - Main class for comprehensive code review operations:
  - Integrates with pyscn for advanced static analysis
  - Provides quality scoring and grading
  - Generates complexity reduction suggestions
  - Checks quality gates
- **`analyze_file(file_path)`** - Analyze a single file for code quality.
- **`analyze_project(project_path)`** - Analyze entire project directory.
- **`check_quality_gates(analysis_result)`** - Validate code against quality thresholds.
- **`generate_report(output_dir)`** - Generate comprehensive HTML/JSON reports.

### analyzer.py
- **`PyscnAnalyzer`** - Specialized analyzer using pyscn for advanced static analysis:
  - `analyze_complexity(file_path)` - Cyclomatic complexity analysis.
  - `detect_dead_code(file_path)` - CFG-based dead code detection.
  - `find_clones(files, threshold)` - Code clone detection with APTED algorithm.
  - `analyze_coupling(file_path)` - Coupling Between Objects (CBO) metrics.
  - `generate_report(output_dir)` - Generate comprehensive pyscn HTML report.

### models.py
- **`QualityDashboard`** - Comprehensive quality metrics dashboard:
  - `overall_score`, `grade`, `analysis_timestamp`
  - Category scores: complexity, maintainability, testability, reliability, security, performance
  - Detailed metrics: complexity, dead_code, duplication, coupling, architecture
  - Top issues and priority recommendations
- **`QualityGateResult`** - Quality gate check results with pass/fail status.
- **`AnalysisResult`** - Individual analysis finding with severity, location, and suggestions.
- **`AnalysisSummary`** - Aggregated analysis statistics.
- **`CodeMetrics`** - Lines of code, cyclomatic complexity, maintainability index.
- **`ComplexityReductionSuggestion`** - Refactoring suggestions for complex functions.
- **`DeadCodeFinding`** - Enhanced dead code finding with removal suggestions.
- **`ArchitectureViolation`** - Architecture compliance violations.

### Enums
- **`AnalysisType`** - Types: QUALITY, SECURITY, PERFORMANCE, MAINTAINABILITY, COMPLEXITY, STYLE, DOCUMENTATION, TESTING, PYSCN.
- **`SeverityLevel`** - Levels: INFO, WARNING, ERROR, CRITICAL.
- **`Language`** - Supported languages: PYTHON, JAVASCRIPT, TYPESCRIPT, JAVA, CPP, CSHARP, GO, RUST, PHP, RUBY.

### Exceptions
- **`CodeReviewError`** - Base exception for code review operations.
- **`PyscnError`** - Error in pyscn analysis.
- **`ToolNotFoundError`** - Required analysis tool not found.
- **`ConfigurationError`** - Invalid configuration provided.

## Operating Contracts

- Pyscn availability is checked before attempting advanced analysis.
- Multiple analysis types can be combined for comprehensive review.
- Quality gates provide pass/fail criteria for CI/CD integration.
- All findings include severity levels and actionable recommendations.
- Reports can be generated in JSON or HTML format.
- Performance monitoring integration available for tracking analysis efficiency.

## Signposting

- **Dependencies**: Optional `pyscn` for advanced analysis (install via `pipx install pyscn`).
- **Parent Directory**: [coding](../README.md) - Parent module documentation.
- **Related Modules**:
  - `execution/` - For testing analyzed code.
  - `debugging/` - For fixing identified issues.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
