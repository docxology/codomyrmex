# Codomyrmex Agents — src/codomyrmex/coding/review

## Signposting
- **Parent**: [coding](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Code review and analysis capabilities. Provides automated code review, quality analysis, security analysis, performance analysis, and maintainability assessment using PySCN and other analysis tools.

## Active Components
- `README.md` – Project file
- `__init__.py` – Module exports and public API
- `analyzer.py` – PySCN-based code analyzer
- `demo_review.py` – Demo review examples
- `models.py` – Data models for analysis results
- `reviewer.py` – Code reviewer implementation

## Key Classes and Functions

### CodeReviewer (`reviewer.py`)
- `CodeReviewer()` – Main code reviewer class
- `analyze_file(file_path: str, analysis_types: Optional[List[AnalysisType]] = None) -> List[AnalysisResult]` – Analyze a single file
- `analyze_project(project_path: str, analysis_types: Optional[List[AnalysisType]] = None) -> AnalysisSummary` – Analyze entire project
- `check_quality_gates(analysis_results: List[AnalysisResult], thresholds: Optional[dict] = None) -> QualityGateResult` – Check quality gates
- `generate_report(analysis_results: List[AnalysisResult], output_path: str, format: str = "json") -> None` – Generate analysis report

### PyscnAnalyzer (`analyzer.py`)
- `PyscnAnalyzer()` – PySCN-based code analyzer
- Analyzes code using PySCN tool

### Data Models (`models.py`)
- `AnalysisResult` (dataclass) – Individual analysis result
- `AnalysisSummary` (dataclass) – Summary of analysis results
- `CodeMetrics` (dataclass) – Code quality metrics
- `QualityGateResult` (dataclass) – Quality gate check results
- `AnalysisType` (Enum) – Types of analysis
- `SeverityLevel` (Enum) – Severity levels

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [coding](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation