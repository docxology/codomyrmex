# BPE Tokenizer -- Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements a from-scratch Byte-Pair Encoding (BPE) tokenizer. Supports training on text corpora, encoding text to token IDs, and decoding IDs back to text with a configurable vocabulary size.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `tokenizer_train` | Train a BPE tokenizer on a list of texts with target vocab size | Standard | tokenizer |
| `tokenizer_encode` | Encode text to BPE token IDs | Standard | tokenizer |
| `tokenizer_decode` | Decode BPE token IDs back to text | Standard | tokenizer |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Train and deploy custom BPE tokenizers for text processing |
| EXECUTE | Engineer Agent | Tokenize and detokenize text for language model pipelines |


## Agent Instructions

1. Call tokenizer_train before encode/decode to build the vocabulary
2. Vocabulary is maintained as a module-level singleton between MCP tool calls


## Navigation

- [Source README](../../src/codomyrmex/tokenizer/README.md) | [SPEC.md](SPEC.md)
