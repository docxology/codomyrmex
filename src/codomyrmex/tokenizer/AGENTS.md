# Tokenizer Module — Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Agent Access Matrix

This document defines which PAI agent types can access tokenizer capabilities and at what trust level.

### Engineer Agent

**Access**: Full access to all operations
**Trust Level**: TRUSTED

| Operation | Capabilities |
|---|---|
| Training | Train BPE on arbitrary corpora, configure vocab size |
| Encoding | Tokenize any text input |
| Decoding | Reconstruct text from token IDs |
| Persistence | Save/load trained tokenizers to JSON |

**Use Cases**: Building tokenization pipelines, preparing text for LLM consumption, measuring token budgets for prompt engineering.

### Architect Agent

**Access**: Read-only analysis
**Trust Level**: OBSERVED

| Operation | Capabilities |
|---|---|
| Encoding | Tokenize text to analyze token distribution |
| Vocabulary | Inspect vocab contents and merge rules |

**Use Cases**: Evaluating tokenization strategies, comparing vocab sizes, analyzing subword granularity for different domains.

### QATester Agent

**Access**: Validation operations
**Trust Level**: OBSERVED

| Operation | Capabilities |
|---|---|
| Encoding | Tokenize test inputs |
| Decoding | Verify round-trip fidelity |
| Training | Train on test corpora for validation |

**Use Cases**: Testing encode/decode round-trip correctness, validating that tokenization handles edge cases (empty strings, unicode, repeated tokens).

### Researcher Agent

**Access**: Full read access
**Trust Level**: OBSERVED

| Operation | Capabilities |
|---|---|
| Training | Train tokenizers on research corpora |
| Encoding | Tokenize for analysis |
| Vocabulary | Inspect learned merge rules |

**Use Cases**: Analyzing BPE behavior on different text distributions, comparing tokenization efficiency across corpora.

## Trust Level Definitions

| Level | Description | Operations Permitted |
|---|---|---|
| UNTRUSTED | No tokenizer access | None |
| OBSERVED | Read-only, analysis | Encode, decode, vocab inspection |
| TRUSTED | Full access | Training, persistence, all operations |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `tokenizer_train` | Train BPE tokenizer on a corpus of texts | SAFE |
| `tokenizer_encode` | Encode text to BPE token IDs | SAFE |
| `tokenizer_decode` | Decode BPE token IDs back to text | SAFE |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `tokenizer_train`, `tokenizer_encode`, `tokenizer_decode` | TRUSTED |
| **Architect** | Read + Analysis | `tokenizer_encode`, `tokenizer_decode` | OBSERVED |
| **QATester** | Validation | `tokenizer_train`, `tokenizer_encode`, `tokenizer_decode` | OBSERVED |
| **Researcher** | Read-only | `tokenizer_train`, `tokenizer_encode`, `tokenizer_decode` | OBSERVED |

## Security Constraints

1. **No persistent state by default**: The module-level tokenizer is ephemeral per process. Persistence requires explicit `save()` call.
2. **No network access**: Training and inference are purely local operations.
3. **No file system side effects**: Only `save()` writes to disk, and only to the specified path.
