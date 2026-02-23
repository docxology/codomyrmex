# coding/review

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive code review and static analysis capabilities. Provides quality assessment, security scanning, complexity analysis, dead code detection, and clone identification. Integrates with pyscn for advanced analysis and traditional tools like pylint, flake8, mypy, and bandit. Supports quality gate checks and HTML/JSON report generation.

## Key Exports

### Models and Data Classes

- **`AnalysisResult`** -- Individual analysis finding with severity, message, and location
- **`AnalysisSummary`** -- Aggregated analysis results across multiple files
- **`AnalysisType`** -- Types of analysis (quality, security, complexity, etc.)
- **`SeverityLevel`** -- Issue severity levels
- **`Language`** -- Supported programming languages
- **`CodeMetrics`** -- Code quality metrics (lines, complexity, etc.)
- **`QualityGateResult`** -- Quality gate check pass/fail results
- **`QualityDashboard`** -- Aggregated quality dashboard data
- **`ArchitectureViolation`** -- Architecture constraint violation finding
- **`ComplexityReductionSuggestion`** -- Suggestion for reducing code complexity
- **`DeadCodeFinding`** -- Dead/unreachable code detection result

### Exceptions

- **`CodeReviewError`** -- Base code review exception
- **`PyscnError`** -- Pyscn analysis errors
- **`ToolNotFoundError`** -- Missing analysis tool
- **`ConfigurationError`** -- Invalid review configuration

### Analyzer

- **`PyscnAnalyzer`** -- Advanced pyscn-based code analysis

### Reviewer

- **`CodeReviewer`** -- Main code review orchestrator; initialized with project_root
- **`analyze_file()`** -- Analyze a single file
- **`analyze_project()`** -- Analyze an entire project directory
- **`check_quality_gates()`** -- Verify quality thresholds are met
- **`generate_report()`** -- Create HTML/JSON review reports

## Directory Contents

- `__init__.py` - Package init; re-exports models, analyzer, and reviewer
- `models.py` - Data classes, enums, and exception definitions
- `analyzer.py` - PyscnAnalyzer implementation
- `reviewer.py` - CodeReviewer, analysis functions, and report generation
- `demo_review.py` - Demonstration/example review script
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [coding](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
