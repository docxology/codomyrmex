# Pattern Matching Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

AST-based pattern matching, design pattern detection, and code similarity analysis for codebases.

## Key Exports

| Export | Source | Description |
|--------|--------|-------------|
| `PatternAnalyzer` | `run_codomyrmex_analysis` | Core pattern analysis engine |
| `PatternMatch` | `run_codomyrmex_analysis` | Individual pattern match result |
| `AnalysisResult` | `run_codomyrmex_analysis` | Aggregate analysis output |
| `ASTMatcher` | `ast_matcher` | AST-based structural pattern matching |
| `ASTMatchResult` | `ast_matcher` | AST match result data |
| `PatternDetector` | `code_patterns` | Design pattern detection (singleton, factory, observer, etc.) |
| `PatternDefinition` | `code_patterns` | Pattern definition schema |
| `PATTERNS` | `code_patterns` | Built-in pattern catalog |
| `CodeSimilarity` | `similarity` | Code similarity and duplicate detection |
| `DuplicateResult` | `similarity` | Duplicate detection result data |

## Submodules

- **`run_codomyrmex_analysis`** -- Core analysis pipeline: repository indexing, dependency analysis, text search, code summarization, docstring indexing, symbol extraction
- **`ast_matcher`** -- AST-based structural pattern matching against Python source
- **`code_patterns`** -- Design pattern detection (singleton, factory, observer, etc.)
- **`similarity`** -- Code similarity scoring and duplicate detection

## Usage

```python
from codomyrmex.coding.pattern_matching import PatternAnalyzer, ASTMatcher, CodeSimilarity

# Analyze repository patterns
analyzer = PatternAnalyzer()
result = analyzer.analyze("path/to/repo")

# AST matching
matcher = ASTMatcher()
matches = matcher.match(source_code, pattern="class_with_singleton")

# Similarity detection
sim = CodeSimilarity()
duplicates = sim.find_duplicates("path/to/repo")
```

## Navigation

- **Parent**: [../README.md](../README.md) -- Coding module
- **Siblings**: [../static_analysis/](../static_analysis/) | [../](../)
- **Root**: [../../../README.md](../../../README.md)
