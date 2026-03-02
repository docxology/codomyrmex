# Tokenizer Module — PAI Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## PAI Algorithm Phase Mapping

The tokenizer module provides text tokenization capabilities that agents can leverage during multiple phases of the PAI Algorithm.

### OBSERVE Phase

**Class**: `BPETokenizer`

- **Token Budget Analysis**: Use `encode()` to measure how many tokens a given text consumes, informing context window management during observation.
- **Vocabulary Inspection**: Examine `vocab` and `merges` to understand what subword units the tokenizer has learned from a domain corpus.

### THINK Phase

**Class**: `BPETokenizer`, `Vocabulary`

- **Tokenization Strategy**: Compare `vocab_size_actual` across different training configurations to reason about the right vocabulary size for a domain.
- **Subword Analysis**: Inspect merge rules to understand which character sequences are most frequent in the domain, informing prompt design decisions.

### BUILD Phase

**MCP Tools**: `tokenizer_train`

- **Train Domain Tokenizer**: Use `tokenizer_train` to build a BPE vocabulary from domain-specific text. Returns vocab size, merge count, and sample tokens.
- **Persistence**: Use `BPETokenizer.save()` to persist trained tokenizers for reuse across sessions.

### EXECUTE Phase

**MCP Tools**: `tokenizer_encode`, `tokenizer_decode`

- **Text Tokenization**: Use `tokenizer_encode` to convert text to token IDs for downstream NLP processing.
- **Text Reconstruction**: Use `tokenizer_decode` to reconstruct human-readable text from token ID sequences.
- **Token Counting**: Use `tokenizer_encode` result's `num_tokens` field to measure prompt lengths against model context limits.

### VERIFY Phase

**MCP Tools**: `tokenizer_encode`, `tokenizer_decode`

- **Round-Trip Validation**: Encode then decode text to verify that tokenization preserves content. Words seen during training should round-trip cleanly.
- **Coverage Verification**: Encode domain-specific text and check for `<UNK>` tokens (ID 1) to verify vocabulary coverage.

## MCP Tools

Three tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `tokenizer_train` | Train a BPE tokenizer on a corpus of texts | Safe | tokenizer |
| `tokenizer_encode` | Encode text to BPE token IDs | Safe | tokenizer |
| `tokenizer_decode` | Decode BPE token IDs back to text | Safe | tokenizer |

## Agent Capabilities

| PAI Agent Type | Primary Operations | Use Case |
|---|---|---|
| Engineer | Train, encode, decode, save/load | Building tokenization pipelines |
| Architect | Encode, vocab inspection | Evaluating tokenization strategies |
| QATester | Train, encode, decode | Validating round-trip correctness |
| Researcher | Train, encode, vocab inspection | Analyzing BPE behavior on corpora |

## Trust Gateway

All tokenizer operations are safe (no file system writes except explicit `save()`, no network access, no code execution). All three MCP tools operate at `SAFE` trust level.
