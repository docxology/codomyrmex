# Logit Processor Tests

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `logit_processor` module. Covers temperature scaling, top-k/top-p filtering, repetition penalty, processor chaining, and token sampling.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestTemperatureProcessor` | Temperature scaling, identity at T=1, sharpening at low T, invalid T |
| `TestTopKProcessor` | Top-k zeroing, larger-than-vocab k, k=1, value preservation |
| `TestTopPProcessor` | Top-p filtering, p=1 keep-all, low-prob filtering, invalid p |
| `TestRepetitionPenalty` | Positive/negative logit penalty, no input_ids, out-of-range IDs |
| `TestLogitProcessorList` | Empty list passthrough, chained processors, append |
| `TestSampleToken` | Token sampling from processed logits |

## Test Structure

```
tests/unit/logit_processor/
    __init__.py
    test_logit_processor.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/logit_processor/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/logit_processor/ --cov=src/codomyrmex/logit_processor -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../logit_processor/README.md)
- [All Tests](../README.md)
