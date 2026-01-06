# Codomyrmex Agents — code/review

## Signposting
- **Parent**: [Code Module](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Siblings**: [execution](../execution/AGENTS.md), [sandbox](../sandbox/AGENTS.md), [monitoring](../monitoring/AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Code review submodule providing automated code review capabilities including quality analysis, best practices checking, and comprehensive code metrics.

## Key Components

- `reviewer.py` – Main code review engine
- `analyzer.py` – Code analysis utilities
- `models.py` – Data models for review results

## Function Signatures

```python
def analyze_file(filepath: str) -> AnalysisResult
def review_code(code: str) -> ReviewResult
```


## Active Components

### Core Files
- `__init__.py` – Package initialization
- Other module-specific implementation files

## Operating Contracts

### Universal Execution Protocols
1. **Comprehensive Analysis** - Analyze all relevant code aspects
2. **Structured Results** - Return structured analysis data
3. **Best Practices** - Check against coding standards
4. **Performance** - Complete analysis within reasonable time

## Navigation Links
- **Parent**: [Code AGENTS](../AGENTS.md)
- **Human Documentation**: [README.md](README.md)
