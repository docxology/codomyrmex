# Tokenizer — MCP Tool Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `tokenizer` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The tokenizer module provides a BPE (Byte Pair Encoding) tokenizer that can be
trained on custom text corpora, then used to encode and decode text.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `tokenizer` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `tokenizer_train`

**Description**: Train a BPE tokenizer on a list of texts.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `texts` | `list[str]` | Yes | -- | List of training strings |
| `vocab_size` | `int` | No | `500` | Target vocabulary size |

**Returns**: `dict` — Dictionary with `status`, `vocab_size` (int, actual vocabulary size achieved), `num_merges` (int), and `sample_vocab` (list of first 20 tokens).

**Example**:
```python
from codomyrmex.tokenizer.mcp_tools import tokenizer_train

result = tokenizer_train(
    texts=["Hello world", "Hello there", "World of tokens"],
    vocab_size=256
)
```

**Notes**: Training replaces the module-level tokenizer instance. Must be called before `tokenizer_encode` or `tokenizer_decode`.

---

### `tokenizer_encode`

**Description**: Encode text to BPE token IDs. Must call `tokenizer_train` first.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | `str` | Yes | -- | Input string to tokenize |

**Returns**: `dict` — Dictionary with `status`, `token_ids` (list of ints), and `num_tokens` (int).

**Example**:
```python
from codomyrmex.tokenizer.mcp_tools import tokenizer_encode

result = tokenizer_encode(text="Hello world")
```

**Notes**: Returns an error status if `tokenizer_train` has not been called yet.

---

### `tokenizer_decode`

**Description**: Decode BPE token IDs back to text.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `token_ids` | `list[int]` | Yes | -- | List of integer token IDs |

**Returns**: `dict` — Dictionary with `status` and `text` (str, the decoded text).

**Example**:
```python
from codomyrmex.tokenizer.mcp_tools import tokenizer_decode

result = tokenizer_decode(token_ids=[72, 101, 108, 108, 111])
```

**Notes**: Returns an error status if `tokenizer_train` has not been called yet.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: BUILD (tokenizer training), EXECUTE (text encoding/decoding)
- **Dependencies**: `tokenizer.bpe.BPETokenizer`
- **Stateful**: The module maintains a global tokenizer instance. `tokenizer_train` must be called before encode/decode operations.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
