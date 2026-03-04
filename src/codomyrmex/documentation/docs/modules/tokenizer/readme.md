# Tokenizer Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Tokenizer module provides a from-scratch Byte-Pair Encoding (BPE) tokenizer implementation with no external dependencies beyond the Python standard library. BPE is the foundational tokenization algorithm used by GPT, RoBERTa, and other modern language models.

The implementation follows the original Sennrich et al. 2016 algorithm: start with a character-level vocabulary, iteratively merge the most frequent adjacent pair until the target vocabulary size is reached.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Train tokenizer on domain-specific corpus | `tokenizer_train` |
| **EXECUTE** | Tokenize text for downstream NLP tasks | `tokenizer_encode` |
| **VERIFY** | Validate encode/decode round-trip fidelity | `tokenizer_encode`, `tokenizer_decode` |

PAI agents use the tokenizer to prepare text for LLM analysis, measure token budgets, and validate that tokenization preserves semantic content.

## Quick Start

### Training a Tokenizer

```python
from codomyrmex.tokenizer import BPETokenizer

corpus = [
    "the quick brown fox jumps over the lazy dog",
    "machine learning and natural language processing",
    "byte pair encoding is a tokenization algorithm",
]

tok = BPETokenizer(vocab_size=200)
tok.train(corpus)
print(f"Vocabulary size: {tok.vocab_size_actual}")
print(f"Merge rules learned: {len(tok.merges)}")
```

### Encoding and Decoding

```python
ids = tok.encode("the quick fox")
print(f"Token IDs: {ids}")

text = tok.decode(ids)
print(f"Decoded: {text}")
```

### Save and Load

```python
tok.save("my_tokenizer.json")
loaded = BPETokenizer.load("my_tokenizer.json")
assert tok.encode("hello") == loaded.encode("hello")
```

### Using the Vocabulary Class

```python
from codomyrmex.tokenizer import Vocabulary

vocab = Vocabulary()
vocab.add("hello")
vocab.add("world")
print(f"Vocab size: {len(vocab)}")
print(f"hello -> {vocab.token_to_id('hello')}")
print(f"ID 5 -> {vocab.id_to_token_str(5)}")
```

## Algorithm Details

### Training Phase

1. **Word frequency counting**: Split corpus on whitespace, represent each word as space-separated characters with an end-of-word marker (`</w>`).
2. **Initial vocabulary**: Special tokens (`<PAD>`, `<UNK>`, `<BOS>`, `<EOS>`) plus all unique characters found in the corpus.
3. **Merge loop**: Count all adjacent token pairs weighted by word frequency. Merge the most frequent pair into a single new token. Repeat until `vocab_size` is reached or no pairs remain.

### Encoding Phase

For each word in the input text:
1. Split into characters plus `</w>` marker.
2. Apply all learned merge rules in order (greedy left-to-right scan).
3. Map resulting tokens to integer IDs via the vocabulary.

### Decoding Phase

Map integer IDs back to token strings, concatenate, and replace `</w>` markers with spaces.

## Dependencies

None beyond the Python standard library (`json`, `collections`, `pathlib`).

## Architecture

The tokenizer module follows Codomyrmex module conventions:

- `bpe.py` — Core `BPETokenizer` class with train/encode/decode/save/load
- `vocab.py` — Standalone `Vocabulary` class for token-ID management
- `mcp_tools.py` — MCP tool definitions for auto-discovery
- No external dependencies (pure Python implementation)
- Foundation layer only (`model_context_protocol` for MCP decorator)

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
