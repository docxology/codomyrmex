# Code Refactoring -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides automated code refactoring operations including symbol renaming, function extraction, and variable inlining. Uses regex-based and AST-aware analysis to generate structured change sets that can be previewed before application.

## Architecture

Abstract base class pattern with `Refactoring` as the base and concrete implementations for each refactoring type. A factory function `create_refactoring` dispatches by `RefactoringType` enum. All refactorings produce a `RefactoringResult` containing a list of `Change` objects that can be applied to files in reverse line order to preserve line numbers.

## Key Classes

### `Refactoring` (Abstract Base Class)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze` | | `list[str]` | Analyzes feasibility and returns warnings |
| `execute` | | `RefactoringResult` | Executes the refactoring and returns changes |
| `preview` | | `str` | Generates a human-readable preview of the changes |

### `RenameRefactoring`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `file_path, old_name, new_name, scope="file"` | `None` | Configures a symbol rename operation |
| `execute` | | `RefactoringResult` | Finds all whole-word occurrences via regex and generates rename changes |

### `ExtractFunctionRefactoring`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `file_path, start_line, end_line, function_name, parameters` | `None` | Configures function extraction from a line range |
| `execute` | | `RefactoringResult` | Extracts code into a new function with detected parameters and return values |

### `InlineRefactoring`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `file_path, symbol_name` | `None` | Configures variable inlining |
| `execute` | | `RefactoringResult` | Finds the definition assignment and replaces all usages with the value |

### Supporting Data Classes

| Class | Fields | Description |
|-------|--------|-------------|
| `RefactoringType` | `RENAME`, `EXTRACT_FUNCTION`, `EXTRACT_CLASS`, `INLINE`, `MOVE`, `ENCAPSULATE_FIELD`, `PULL_UP`, `PUSH_DOWN`, `REPLACE_CONDITIONAL` | Enum of refactoring types |
| `Location` | `file_path`, `line`, `column`, `end_line`, `end_column` | Source code location |
| `Change` | `location`, `old_text`, `new_text`, `description` | A single code change |
| `RefactoringResult` | `success`, `changes`, `description`, `warnings`, `errors` | Result with `apply_to_files()` method |

### Factory Function

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `create_refactoring` | `refactoring_type: RefactoringType, **kwargs` | `Refactoring` | Factory dispatching to concrete refactoring class |

## Dependencies

- **Internal**: None (self-contained within `coding` package)
- **External**: `ast` (stdlib), `re` (stdlib), `pathlib` (stdlib)

## Constraints

- Rename uses whole-word regex matching (`\b...\b`), not AST-aware scope analysis.
- Extract function detects parameters via regex-based variable analysis, not full AST.
- `apply_to_files` applies changes in reverse line order to preserve line numbers.
- Only `RENAME`, `EXTRACT_FUNCTION`, and `INLINE` are implemented; other types raise `ValueError`.
- Zero-mock: real file operations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Refactoring failures return `RefactoringResult(success=False, errors=[...])` rather than raising exceptions.
- Warnings for shadowed builtins and existing names are returned in the result's `warnings` list.
