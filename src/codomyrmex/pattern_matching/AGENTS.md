# Agent Guidelines - Pattern Matching

## Module Overview

Code analysis through AST parsing, pattern recognition, and embeddings.

## Key Classes

- **PatternAnalyzer** — Analyze code patterns
- **ASTParser** — Parse code to AST
- **EmbeddingGenerator** — Generate code embeddings
- **SimilarityFinder** — Find similar code

## Agent Instructions

1. **Parse first** — Use AST for structural analysis
2. **Cache embeddings** — Compute once, reuse often
3. **Normalize code** — Remove formatting variations
4. **Set thresholds** — Configure similarity thresholds
5. **Batch process** — Use batch embedding for large codebases

## Common Patterns

```python
from codomyrmex.pattern_matching import (
    PatternAnalyzer, EmbeddingGenerator, SimilarityFinder, analyze_code
)

# Quick analysis
result = analyze_code("path/to/file.py")
print(f"Patterns found: {result.patterns}")
print(f"Complexity: {result.complexity}")

# Pattern analyzer
analyzer = PatternAnalyzer()
patterns = analyzer.find_patterns(code, pattern_type="function")

# Embedding-based similarity
embedder = EmbeddingGenerator()
embedding = embedder.generate(code_snippet)

finder = SimilarityFinder()
similar = finder.find_similar(embedding, codebase, top_k=5)
for match in similar:
    print(f"{match.file}:{match.line} - {match.similarity:.2f}")
```

## Testing Patterns

```python
# Verify pattern detection
analyzer = PatternAnalyzer()
patterns = analyzer.find_patterns("def foo(): pass")
assert len(patterns) > 0

# Verify embedding generation
embedder = EmbeddingGenerator()
emb = embedder.generate("def foo(): return 1")
assert len(emb) > 0  # Non-empty embedding
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
