# SLM (Small Language Model) Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `slm` module. Covers causal masking, SLM configuration, forward pass (output shape, logit finiteness, max sequence length), generation (prompt preservation, vocab range, determinism), and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestCausalMask` | Causal mask shape, lower-triangular, diagonal, upper triangle, size=1 |
| `TestSLMConfig` | Default and custom config values |
| `TestSLMForward` | Forward output shape, single token, logit finiteness, callable, max_seq_len error |
| `TestSLMGenerate` | Generate returns list, correct length, prompt preserved, vocab range, determinism |
| `TestMCPTools` | slm_generate and slm_forward MCP tools and metadata |

## Test Structure

```
tests/unit/slm/
    __init__.py
    test_slm.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/slm/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/slm/ --cov=src/codomyrmex/slm -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../slm/README.md)
- [All Tests](../README.md)
