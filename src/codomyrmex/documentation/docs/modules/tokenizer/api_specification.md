# Tokenizer - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `tokenizer` module provides a from-scratch Byte-Pair Encoding (BPE) tokenizer implementation with vocabulary management. Suitable for training custom tokenizers on domain-specific corpora.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `BPETokenizer` | Full BPE tokenizer with training, encoding, and decoding |
| `Vocabulary` | Vocabulary management with token-to-ID mapping and special tokens |

## 3. Usage Example

```python
from codomyrmex.tokenizer import BPETokenizer

tokenizer = BPETokenizer(vocab_size=8192)
tokenizer.train(["The quick brown fox.", "Machine learning is great."])

encoded = tokenizer.encode("The quick brown fox.")
decoded = tokenizer.decode(encoded)
print(f"Tokens: {encoded}, Decoded: {decoded}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
