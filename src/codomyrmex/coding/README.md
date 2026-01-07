# coding

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [debugging](debugging/README.md)
    - [docs](docs/README.md)
    - [execution](execution/README.md)
    - [monitoring](monitoring/README.md)
    - [review](review/README.md)
    - [sandbox](sandbox/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Unified interface for code execution, sandboxing, review, and monitoring. Consolidates secure code execution and automated code review capabilities into a cohesive structure with support for multiple programming languages, Docker-based sandboxing, resource limits, quality gates, and comprehensive analysis types (quality, security, performance, maintainability).

## Directory Contents
- `MIGRATION_COMPLETE.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `debugging/` – Subdirectory
- `docs/` – Subdirectory
- `execution/` – Subdirectory
- `monitoring/` – Subdirectory
- `review/` – Subdirectory
- `sandbox/` – Subdirectory
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.coding.execution import execute_code
from codomyrmex.coding.sandbox import run_code_in_docker, ExecutionLimits
from codomyrmex.coding.review import CodeReviewer, analyze_file
from codomyrmex.coding.monitoring import ExecutionMonitor

# Execute code in sandbox
limits = ExecutionLimits(cpu_time=5.0, memory_mb=512)
result = execute_code(
    code="print('Hello, World!')",
    language="python",
    limits=limits
)
print(f"Output: {result.output}")

# Review code
reviewer = CodeReviewer()
review = analyze_file("src/my_module.py")
print(f"Issues: {len(review.issues)}")

# Monitor execution
monitor = ExecutionMonitor()
with monitor.track_execution("my_function"):
    result = my_function()
print(f"Execution time: {monitor.get_metrics().execution_time}s")
```

