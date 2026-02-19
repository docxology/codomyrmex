# coding/refactoring

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Automated code refactoring patterns and transformations. Provides a framework for analyzing, previewing, and executing refactoring operations on Python source code. Currently implements rename (whole-word replacement with scope control), extract function (with automatic variable detection), and inline (variable substitution) refactorings. Each refactoring supports a three-phase workflow: analyze (warnings), preview (dry run), and execute (produce changes).

## Key Exports

### Enums

- **`RefactoringType`** -- Refactoring operation types (RENAME, EXTRACT_FUNCTION, EXTRACT_CLASS, INLINE, MOVE, ENCAPSULATE_FIELD, PULL_UP, PUSH_DOWN, REPLACE_CONDITIONAL)

### Data Classes

- **`Location`** -- Source code location with file_path, line, column, and optional end positions
- **`Change`** -- A single code change with location, old_text, new_text, and description; includes `to_dict()` serialization
- **`RefactoringResult`** -- Result of a refactoring operation with success flag, list of changes, description, warnings, and errors; includes `apply_to_files()` to write changes to disk

### Abstract Base

- **`Refactoring`** -- ABC defining `analyze()`, `execute()`, and `preview()` interface for all refactoring operations

### Refactoring Implementations

- **`RenameRefactoring`** -- Rename a symbol (variable, function, class) with whole-word matching, builtin shadowing detection, and file/module/project scope
- **`ExtractFunctionRefactoring`** -- Extract a line range into a new function with automatic parameter and return value detection via regex-based variable analysis
- **`InlineRefactoring`** -- Inline a variable by replacing all usages with its assigned value; warns when usage count is high

### Factory

- **`create_refactoring()`** -- Factory function to instantiate refactorings by `RefactoringType` with kwargs

## Directory Contents

- `__init__.py` - Package init; contains all refactoring classes inline (single-file module)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [coding](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
