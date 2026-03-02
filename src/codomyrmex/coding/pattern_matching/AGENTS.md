# Codomyrmex Agents -- src/codomyrmex/coding/pattern_matching

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Design-pattern detection, AST-based anti-pattern discovery, token-level code similarity analysis, and repository-wide pattern analytics. Provides both structural matching (via Python `ast`) and embedding-backed search for code summarization, symbol extraction, and duplicate detection.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `ast_matcher.py` | `ASTMatcher` | Walks Python AST to find design patterns (singleton, factory, decorator, context_manager) and anti-patterns (bare_except, mutable_default_arg, star_import, nested_function_depth) |
| `ast_matcher.py` | `ASTMatchResult` | Dataclass holding pattern name, matched node, line range, and confidence score |
| `code_patterns.py` | `PatternDetector` | Registry-based detector; iterates `PATTERNS` dict and applies each pattern's AST visitor to source code |
| `code_patterns.py` | `PatternDefinition` | Dataclass describing a pattern: name, description, AST node types, detection callable |
| `code_patterns.py` | `PATTERNS` | Built-in catalog of six patterns: singleton, factory, observer, strategy, decorator_pattern, template_method |
| `similarity.py` | `CodeSimilarity` | Token-based cosine similarity plus structural AST hashing for duplicate detection |
| `similarity.py` | `DuplicateResult` | Dataclass: file pair, similarity score, shared token count |
| `run_codomyrmex_analysis.py` | `PatternAnalyzer` | Orchestrates full-repository analysis combining pattern detection, similarity, and embedding search |
| `run_codomyrmex_analysis.py` | `PatternMatch`, `AnalysisResult` | Dataclasses for individual match results and aggregate analysis output |
| `run_codomyrmex_analysis.py` | `_perform_*` helpers | Repository indexing, dependency analysis, text search, code summarization, docstring indexing, symbol extraction, symbol usage analysis |
| `__init__.py` | `cli_commands()` | Click CLI group exposing pattern-matching operations |

## Operating Contracts

- `ASTMatcher.parse_code()` requires valid Python source; raises `SyntaxError` on unparseable input.
- `PatternDetector.register_pattern()` accepts a `PatternDefinition` with a callable that receives an `ast.AST` node and returns `bool`.
- `CodeSimilarity.compute_similarity()` returns a float in `[0.0, 1.0]`; 1.0 means identical token sequences.
- `find_duplicates()` accepts a `threshold` parameter (default 0.8) below which pairs are excluded.
- `PatternAnalyzer` helpers (`_perform_*`) require an embedding function obtained via `get_embedding_function()`.
- Errors are logged via `logging_monitoring` before propagation.

## Integration Points

- **Depends on**: Python `ast` stdlib, `logging_monitoring`, optional embedding providers
- **Used by**: `coding` package exports, `coding.mcp_tools` (MCP tool surface), CI pipelines for pattern audits

## Navigation

- **Parent**: [coding](../README.md)
- **Sibling**: [review](../review/README.md), [static_analysis](../static_analysis/README.md), [parsers](../parsers/README.md)
- **Root**: [Root](../../../../../README.md)
