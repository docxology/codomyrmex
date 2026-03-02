# Codomyrmex Agents -- src/codomyrmex/coding/static_analysis/linting

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Pluggable rule-based linter using the Strategy pattern. Defines a `LintRule` abstract base class that concrete rules implement, and a `Linter` orchestrator that applies registered rules to source files. Ships with four built-in rules; additional rules can be registered at runtime.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `Linter` | Orchestrator: registers rules, runs them against source, returns `LintResult` |
| `__init__.py` | `LintRule` (ABC) | Abstract base class; subclasses implement `check(source: str, file_path: str) -> list[LintIssue]` |
| `__init__.py` | `LineLengthRule` | Flags lines exceeding configurable max length (default 120) |
| `__init__.py` | `TrailingWhitespaceRule` | Flags lines with trailing whitespace |
| `__init__.py` | `UnusedImportRule` | Detects import statements whose names do not appear in the rest of the file |
| `__init__.py` | `TodoCommentRule` | Flags TODO, FIXME, HACK, XXX comments |
| `__init__.py` | `LintSeverity` | Enum: ERROR, WARNING, INFO |
| `__init__.py` | `LintIssue` | Dataclass: rule name, severity, message, line number, column |
| `__init__.py` | `LintResult` | Dataclass: file path, list of issues, pass/fail flag |

## Operating Contracts

- `LintRule` subclasses must implement `check(source: str, file_path: str) -> list[LintIssue]`.
- `Linter.register_rule()` accepts any `LintRule` instance; rules are applied in registration order.
- `Linter.lint_file()` reads the file, applies all registered rules, returns `LintResult`.
- `Linter.lint_directory()` walks `.py` files recursively, returns `list[LintResult]`.
- `LintResult.passed` is `True` when no issues with `LintSeverity.ERROR` are found.
- Rules are stateless; each `check()` call is independent.

## Integration Points

- **Depends on**: Python `re` stdlib (for pattern matching in rules)
- **Used by**: `static_analysis.StaticAnalyzer`, `coding` package CLI commands

## Navigation

- **Parent**: [static_analysis](../README.md)
- **Sibling**: [complexity](../complexity/)
- **Root**: [Root](../../../../../../README.md)
