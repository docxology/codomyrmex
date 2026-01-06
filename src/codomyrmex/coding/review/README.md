# Code Review Submodule

## Signposting
- **Parent**: [Code Module](../README.md)
- **Siblings**: [execution](../execution/), [sandbox](../sandbox/), [monitoring](../monitoring/)
- **Key Artifacts**: [AGENTS.md](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The review submodule provides automated code review capabilities including quality analysis, best practices checking, and comprehensive code metrics.

## Key Components

### reviewer.py
Main code review engine with comprehensive analysis capabilities.

### analyzer.py
Code analysis utilities for metrics, complexity, and quality assessment.

### models.py
Data models for review results, analysis summaries, and code metrics.

## Usage

```python
from codomyrmex.coding.review import CodeReviewer, analyze_file

# Analyze a single file
result = analyze_file("path/to/file.py")

# Create reviewer instance
reviewer = CodeReviewer()
review_result = reviewer.review_code(code_content)
```

## Navigation Links

- **Parent**: [Code Module](../README.md)
- **Code AGENTS**: [../AGENTS.md](../AGENTS.md)
- **Source Root**: [src/codomyrmex](../../README.md)
