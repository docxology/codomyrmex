# Linting -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pluggable Python-native linter using the Strategy pattern. Each lint rule is a `LintRule` subclass with a `check()` method. The `Linter` class manages rule registration, file reading, and result aggregation. Designed for extensibility: custom rules can be added at runtime without modifying existing code.

## Architecture

Strategy pattern in a single module (`__init__.py`, ~242 lines):

1. **LintRule ABC** -- defines the `check(source, file_path) -> list[LintIssue]` interface.
2. **Concrete rules** -- four built-in implementations (line length, trailing whitespace, unused imports, TODO comments).
3. **Linter** -- orchestrator that maintains a rule registry and applies all rules to files.

## Key Classes

### `Linter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_rule` | `rule: LintRule` | `None` | Add a rule to the registry |
| `lint_file` | `file_path: str` | `LintResult` | Read file and run all registered rules |
| `lint_directory` | `dir_path: str, extensions: list[str] = [".py"]` | `list[LintResult]` | Recursive linting of matching files |

### `LintRule` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `check` | `source: str, file_path: str` | `list[LintIssue]` | Abstract: detect issues in source |
| `name` | _(property)_ | `str` | Rule identifier (e.g., `"line-length"`) |

### Built-in Rules

| Rule Class | Default Config | Severity | What It Checks |
|-----------|---------------|----------|----------------|
| `LineLengthRule` | `max_length=120` | WARNING | Lines exceeding max character count |
| `TrailingWhitespaceRule` | _(none)_ | WARNING | Lines ending with spaces or tabs |
| `UnusedImportRule` | _(none)_ | WARNING | Import names not referenced in file body |
| `TodoCommentRule` | _(none)_ | INFO | Comments containing TODO, FIXME, HACK, XXX |

## Data Types

| Type | Fields | Notes |
|------|--------|-------|
| `LintSeverity` | ERROR, WARNING, INFO | Enum |
| `LintIssue` | `rule`, `severity`, `message`, `line`, `column` | Single finding |
| `LintResult` | `file_path`, `issues: list[LintIssue]`, `passed: bool` | Per-file aggregate; `passed` is `True` when no ERROR-level issues |

## Dependencies

- **Internal**: None
- **External**: Python `re` stdlib

## Constraints

- Rules are stateless; `check()` receives source text and path, returns issues.
- `LineLengthRule.max_length` is set at construction time and immutable.
- `UnusedImportRule` uses simple name matching (not scope-aware); may produce false positives for re-exports.
- File encoding assumed UTF-8; `UnicodeDecodeError` propagates to caller.
- Zero-mock: real source files required for linting.

## Extensibility

Custom rules follow this pattern:

```python
class MyRule(LintRule):
    @property
    def name(self) -> str:
        return "my-custom-rule"

    def check(self, source: str, file_path: str) -> list[LintIssue]:
        issues = []
        # detection logic
        return issues

linter = Linter()
linter.register_rule(MyRule())
```
