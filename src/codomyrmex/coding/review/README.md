# review

## Signposting
- **Parent**: [coding](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Code review and analysis capabilities. Provides automated code review, quality analysis, security analysis, performance analysis, and maintainability assessment using PySCN and other analysis tools.

## Directory Contents
- `README.md` – File
- `__init__.py` – File
- `analyzer.py` – File
- `demo_review.py` – File
- `models.py` – File
- `reviewer.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [coding](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.coding.review import (
    CodeReviewer,
    analyze_file,
    analyze_project,
    check_quality_gates,
)

# Review a single file
reviewer = CodeReviewer()
result = analyze_file("src/my_module.py")
print(f"Issues found: {len(result.issues)}")
for issue in result.issues:
    print(f"  - {issue.severity}: {issue.message}")

# Review entire project
project_result = analyze_project("src/")
print(f"Project metrics: {project_result.summary}")

# Check quality gates
gate_result = check_quality_gates(project_result)
if gate_result.passed:
    print("Quality gates passed!")
else:
    print(f"Quality gates failed: {gate_result.failures}")
```

