# Agent Guidelines - Coding

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Unified toolkit for code execution, analysis, review, and transformation.

## Key Classes

- **CodeReviewer** — Orchestrate code quality reviews
- **StaticAnalyzer** — Run deep linting and complexity analysis
- **PatternMatcher** — Search for structural patterns (AST-based)
- **CodeGenerator** — Generate code from functional specs
- **Debugger** — Automated error diagnosis and patching

## Agent Instructions

1. **Analyze before fix** — Use `StaticAnalyzer` to verify code quality before suggesting fixes
2. **Structural Search** — Use `PatternMatcher` to find all instances of a pattern before refactoring
3. **Sandbox execution** — Always use `coding.execution` for untrusted code
4. **Metric-driven review** — Check `CodeMetrics` during reviews

## Common Patterns

```python
from codomyrmex.coding import (
    CodeReviewer, StaticAnalyzer, PatternMatcher, Debugger
)

# Deep Static Analysis
analyzer = StaticAnalyzer()
results = analyzer.analyze_project("./src")
print(f"Complexity: {results.complexity}")

# Find occurrences of a pattern
matcher = PatternMatcher()
occurrences = matcher.find_pattern(
    "Assignment(target=Name(id='x'), value=Constant(value=1))"
)

# Automated Debug Loop
debugger = Debugger()
diagnosis = debugger.diagnose(failing_script_path)
if diagnosis.can_fix:
    patch = debugger.generate_patch(diagnosis)
    debugger.apply_and_verify(patch)
```

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `code_execute` | Execute code in a sandboxed environment (Python, JavaScript, etc.) | `language`, `code`, `timeout` (default 30) | Destructive |
| `code_list_languages` | List all supported programming languages for code execution | (none) | Safe |
| `code_review_file` | Analyze a Python file for quality metrics, complexity, and issues | `path` | Safe |
| `code_review_project` | Analyze a project directory for code quality and architecture violations | `path` | Safe |
| `code_debug` | Analyze an error and suggest fixes using the Debugger | `code`, `stdout`, `stderr`, `exit_code` | Safe |

## Testing Patterns

```python
# Verify static analysis findings
analyzer = StaticAnalyzer()
results = analyzer.analyze_file("bad_code.py")
assert any(r.type == "Complexity" for r in results)

# Verify pattern matching
matcher = PatternMatcher()
matches = matcher.find_in_string("x = 10", "Assignment")
assert len(matches) == 1
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full sandbox | `code_execute` (Destructive), `code_review_file`, `code_review_project`, `code_debug` | TRUSTED |
| **Architect** | Project review | `code_review_project` | OBSERVED |
| **QATester** | Execution + Debug | `code_execute`, `code_debug` | OBSERVED |
| **Researcher** | Review-only | `code_review_file`, `code_list_languages` | OBSERVED |

### Engineer Agent
**Access**: Full — sandbox execution and all review/debug tools.
**Use Cases**: Executing generated code in the BUILD phase, debugging failing implementations, reviewing code quality after refactoring, running language-specific tests.

### Architect Agent
**Access**: Project-level review — architecture and quality analysis without execution.
**Use Cases**: Evaluating project-level code quality metrics, identifying architectural violations, assessing complexity distribution across modules.

### QATester Agent
**Access**: Execution and debugging — running tests and diagnosing failures.
**Use Cases**: Executing test suites against BUILD output, diagnosing test failures with `code_debug`, verifying exit codes and stdout match expected VERIFY criteria.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
