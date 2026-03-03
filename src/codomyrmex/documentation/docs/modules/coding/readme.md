# coding

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unified module for code execution, sandboxing, review, monitoring, and debugging. Provides a comprehensive toolkit for running, analyzing, and fixing code programmatically. Contains six submodules: `execution`, `sandbox`, `review`, `monitoring`, `debugging`, and two consolidated sub-packages (`pattern_matching`, `static_analysis`).

## PAI Integration

| PAI Phase | Capability |
|-----------|-----------|
| BUILD | `execute_code()` runs code in sandboxed environments |
| VERIFY | `CodeReviewer` analyzes quality; `analyze_file()` / `analyze_project()` scan for issues |
| THINK | `Debugger` analyzes errors and generates patches |

## Key Exports

- **`execute_code(language, code, timeout)`** -- Execute code in a sandboxed environment
- **`CodeReviewer`** -- Main code review orchestrator
- **`Debugger`** -- Automated error analysis and fix generation
- **`ErrorAnalyzer`**, **`PatchGenerator`**, **`FixVerifier`** -- Debug pipeline components
- **`analyze_file()`**, **`analyze_project()`** -- Static analysis convenience functions
- **`check_quality_gates()`** -- Verify quality thresholds
- **`generate_report()`** -- Produce HTML/JSON review reports
- **`ExecutionLimits`**, **`run_code_in_docker()`** -- Sandbox isolation
- **`ExecutionMonitor`**, **`MetricsCollector`**, **`ResourceMonitor`** -- Execution tracking

## MCP Tools

| Tool | Description |
|------|-------------|
| `code_execute` | Execute code in a sandboxed environment |
| `code_list_languages` | List supported programming languages |
| `code_review_file` | Analyze a Python file for quality metrics |
| `code_review_project` | Analyze a project directory for quality and architecture |
| `code_debug` | Analyze an error and suggest fixes |

## Quick Start

```python
from codomyrmex.coding import execute_code, CodeReviewer, Debugger

result = execute_code("python", "print('Hello!')")

reviewer = CodeReviewer("./src")
issues = reviewer.analyze_file("module.py")

debugger = Debugger()
fixed = debugger.debug(code, stdout, stderr, exit_code=1)
```

## Architecture

```
coding/
  execution/       -- Sandboxed code execution with multi-language support
  sandbox/         -- Container isolation and resource limits
  review/          -- Static analysis and code quality assessment
    mixins/        -- Analysis mixin classes (9 mixins)
    reviewer_impl/ -- CodeReviewer decomposition (5 mixins)
  monitoring/      -- Execution metrics and resource tracking
  debugging/       -- Automated error analysis and fix generation
  pattern_matching/ -- Code pattern recognition
  static_analysis/ -- Code quality, linting, security scanning
  mcp_tools.py     -- MCP tool definitions (5 tools)
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/coding/ -v
```

## Navigation

- [Root](../../../../../../README.md)
