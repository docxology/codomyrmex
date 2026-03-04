# BPE Tokenizer Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements a from-scratch Byte-Pair Encoding (BPE) tokenizer. Supports training on text corpora, encoding text to token IDs, and decoding IDs back to text with a configurable vocabulary size.

## Functional Requirements

1. BPE training from text corpora with iterative merge-pair frequency counting
2. Encoding text to integer token IDs using the trained merge table
3. Decoding token IDs back to text using the inverse vocabulary mapping


## Interface

```python
from codomyrmex.tokenizer import BPETokenizer, Vocabulary

tok = BPETokenizer(vocab_size=500)
tok.train(["Hello world", "BPE tokenization example"])
ids = tok.encode("Hello world")
text = tok.decode(ids)
```

## Exports

BPETokenizer, Vocabulary

## Navigation

- [Source README](../../src/codomyrmex/tokenizer/README.md) | [AGENTS.md](AGENTS.md)
