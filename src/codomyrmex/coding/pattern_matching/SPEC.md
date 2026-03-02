# Pattern Matching -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Structural code analysis using Python's `ast` module for design-pattern and anti-pattern detection, token-level cosine similarity for duplicate discovery, and embedding-backed helpers for repository-wide code search and summarization.

## Architecture

Three complementary engines, each independently usable:

1. **AST Matcher** (`ASTMatcher`) -- walks a parsed AST and returns `ASTMatchResult` objects for known patterns and anti-patterns.
2. **Pattern Detector** (`PatternDetector`) -- registry of `PatternDefinition` entries; applies each definition's detection callable across source files.
3. **Code Similarity** (`CodeSimilarity`) -- tokenizes source, computes cosine similarity, and produces `DuplicateResult` pairs above a configurable threshold.

`PatternAnalyzer` in `run_codomyrmex_analysis.py` orchestrates all three plus embedding-based helpers for full-repository analytics.

## Key Classes

### `ASTMatcher`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse_code` | `source: str` | `ast.Module` | Parse Python source into AST; raises `SyntaxError` |
| `find_pattern` | `tree: ast.Module, pattern: str` | `list[ASTMatchResult]` | Find named pattern (singleton, factory, decorator, context_manager) |
| `find_antipatterns` | `tree: ast.Module` | `list[ASTMatchResult]` | Detect bare_except, mutable_default_arg, star_import, nested_function_depth |
| `match_structure` | `tree: ast.Module, template: ast.AST` | `list[ASTMatchResult]` | Structural subtree matching against an AST template |

### `PatternDetector`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `detect_patterns` | `source: str` | `list[PatternMatch]` | Run all registered patterns against source |
| `register_pattern` | `definition: PatternDefinition` | `None` | Add a custom pattern to the registry |

### `CodeSimilarity`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `compute_similarity` | `source_a: str, source_b: str` | `float` | Token cosine + structural hash; returns `[0.0, 1.0]` |
| `find_duplicates` | `files: list[str], threshold: float = 0.8` | `list[DuplicateResult]` | All file pairs above threshold |
| `structural_hash` | `source: str` | `str` | SHA-256 of normalized AST structure |

## Data Types

| Type | Fields | Notes |
|------|--------|-------|
| `ASTMatchResult` | `pattern_name`, `node`, `start_line`, `end_line`, `confidence` | Confidence is `float` in `[0.0, 1.0]` |
| `PatternDefinition` | `name`, `description`, `node_types`, `detect_fn` | `detect_fn` signature: `(ast.AST) -> bool` |
| `DuplicateResult` | `file_a`, `file_b`, `similarity`, `shared_tokens` | Similarity is `float` in `[0.0, 1.0]` |
| `PatternMatch` | `pattern_name`, `file_path`, `line`, `confidence` | Result from `PatternDetector` |
| `AnalysisResult` | `matches`, `duplicates`, `summary` | Aggregate output from `PatternAnalyzer` |

## Built-in Patterns (PATTERNS dict)

| Key | Description | AST Signal |
|-----|-------------|------------|
| `singleton` | Class with `_instance` attribute and `__new__` override | `ast.ClassDef` with `_instance` in assignments |
| `factory` | Function or method returning different types based on input | `ast.FunctionDef` with multiple `ast.Return` of different types |
| `observer` | Subject/observer with subscribe/notify methods | `ast.ClassDef` with `subscribe`/`notify` methods |
| `strategy` | Abstract strategy base with concrete implementations | ABC subclass pattern with overridden method |
| `decorator_pattern` | Wrapper class delegating to wrapped component | `ast.ClassDef` with `__init__` storing a component reference |
| `template_method` | Base class with abstract steps and concrete orchestrator | `ast.ClassDef` with mix of abstract and concrete methods |

## Dependencies

- **Internal**: `logging_monitoring`
- **External**: Python `ast` stdlib, `tokenize`, optional embedding providers

## Constraints

- AST-based detection is Python-only; other languages require tree-sitter parsers.
- Similarity computation is O(n^2) over file pairs; use `threshold` to prune.
- `get_embedding_function()` returns `None` when no embedding provider is configured; `PatternAnalyzer` helpers degrade gracefully.
- Zero-mock: real AST trees and real source files required for all operations.

## Error Handling

- `ASTMatcher.parse_code()` raises `SyntaxError` for invalid Python source.
- `CodeSimilarity` returns `0.0` similarity for files that fail to tokenize.
- `PatternAnalyzer` logs and skips files that cannot be read, continuing with remaining files.
