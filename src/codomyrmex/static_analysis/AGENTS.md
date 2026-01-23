# Codomyrmex Agents — src/codomyrmex/static_analysis

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Core Layer module providing tools and integrations for analyzing source code without executing it. Enhances code quality through automated analysis and error detection across multiple programming languages.

## Active Components

### Main Analyzer

- `static_analyzer.py` - Main analyzer implementation
  - Key Classes: `StaticAnalyzer`, `AnalysisResult`, `AnalysisSummary`, `CodeMetrics`
  - Key Functions: `analyze_file()`, `analyze_project()`, `get_available_tools()`

### Pyrefly Integration

- `pyrefly_runner.py` - Pyrefly analysis runner
  - Key Classes: `PyreflyRunner`, `PyreflyResult`, `PyreflyIssue`
  - Key Functions: `run_pyrefly()`, `check_pyrefly_available()`

### Data Structures

- `AnalysisType` - Enum: quality, security, performance, style, complexity
- `SeverityLevel` - Enum: info, warning, error, critical
- `Language` - Enum: supported programming languages

## Key Classes and Functions

| Class/Function | Purpose |
| :--- | :--- |
| `StaticAnalyzer` | Main analyzer orchestrating all analysis tools |
| `analyze_file(filepath)` | Analyze a single file for various issues |
| `analyze_project(path)` | Analyze an entire project |
| `get_available_tools()` | List available analysis tools |
| `PyreflyRunner` | Run Pyrefly type checking |
| `AnalysisResult` | Individual analysis finding |
| `AnalysisSummary` | Aggregated analysis results |
| `CodeMetrics` | Computed code quality metrics |

## Operating Contracts

1. **Logging**: Uses `logging_monitoring` for all analysis logging
2. **Environment**: Relies on `environment_setup` for dependency checks
3. **Integration**: Results integrate with `coding/review` for combined analysis
4. **MCP Tools**: Exposes MCP-compatible analysis tools
5. **Multi-Language**: Supports Python, JavaScript, Go, Rust, Java

## Usage Example

```python
from codomyrmex.static_analysis import (
    StaticAnalyzer,
    analyze_project,
    AnalysisType
)

# Quick analysis
results = analyze_project("./src", analysis_types=[AnalysisType.QUALITY])

# Full analyzer
analyzer = StaticAnalyzer()
summary = analyzer.analyze("./src", include_metrics=True)
print(f"Issues found: {summary.total_issues}")
```

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| coding | [../coding/AGENTS.md](../coding/AGENTS.md) | Code execution and review |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security scanning |
| pattern_matching | [../pattern_matching/AGENTS.md](../pattern_matching/AGENTS.md) | Pattern recognition |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tools
- [SPEC.md](SPEC.md) - Functional specification
