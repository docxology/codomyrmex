# Tokenizer Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `tokenizer` module. Covers BPE training (vocab, merges, special tokens, single word, empty corpus), encoding/decoding (round-trip, multiword, unknown chars), save/load persistence, and vocabulary management.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestBPETraining` | Vocab production, special tokens, non-empty merges, frequent pair merge, vocab size override, empty/single corpus |
| `TestBPEEncoding` | Encode returns ints, non-empty, decode string, round-trip, multiword, unknown chars, untrained raises |
| `TestBPESaveLoad` | Save and load round-trip, file creation, merge preservation |
| `TestVocabulary` | Initial special tokens, add token, duplicate ID, unknown token/ID, length growth |

## Test Structure

```
tests/unit/tokenizer/
    __init__.py
    test_tokenizer.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/tokenizer/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/tokenizer/ --cov=src/codomyrmex/tokenizer -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../tokenizer/README.md)
- [All Tests](../README.md)
