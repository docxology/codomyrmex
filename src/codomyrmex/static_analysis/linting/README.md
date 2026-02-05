# linting

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Code linting and quality checks with a pluggable rule system. Provides `Linter` with built-in rules for line length (E501), trailing whitespace (W291), unused imports (F401), and TODO/FIXME comments (W999). Supports custom rules via the `LintRule` abstract base class.

## Key Exports

- **`Linter`** — Main linter with `lint(content)` and `lint_file(path)` returning `LintResult`. Ships with 4 default rules. Extensible via `add_rule()`.
- **`LintRule`** — Abstract base class for custom rules. Subclass with `id`, `message`, and `check(content, file_path)` methods.
- **`LineLengthRule`** — Checks lines exceeding max length (default 120 chars, rule E501)
- **`TrailingWhitespaceRule`** — Detects trailing whitespace (rule W291)
- **`UnusedImportRule`** — AST-based unused import detection (rule F401)
- **`TodoCommentRule`** — Finds TODO/FIXME/XXX/HACK comments (rule W999)
- **`LintIssue`** — Dataclass: rule_id, message, severity, category, file_path, line_number, column, code_snippet, suggestion
- **`LintResult`** — Dataclass: file_path, issues list, error/warning/info counts. Properties `has_errors` and `total_issues`.
- **`LintSeverity`** — Enum: `ERROR`, `WARNING`, `INFO`, `HINT`
- **`LintCategory`** — Enum: `STYLE`, `CONVENTION`, `ERROR`, `WARNING`, `REFACTOR`

## Navigation

- **Parent Module**: [static_analysis](../README.md)
- **Parent Directory**: [codomyrmex](../../README.md)
