# PEFT (Parameter-Efficient Fine-Tuning) Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `peft` module. Covers LoRA adapter (zero-init, output shapes, trainable params), prefix tuning (token prepending, layer keys/values), IA3 adapter (ones init, scaling, modes), parameter efficiency comparisons, and PEFT config.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestLoRAAdapter` | LoRA B zero-init, base output, nonzero B output, shape, trainable params, scaling, A/B shapes |
| `TestPrefixTuningAdapter` | Prefix prepending, original preservation, layer keys, trainable params, batch dimension |
| `TestIA3Adapter` | IA3 ones-init no change, nonzero scaling, trainable params, default d_ff, unknown mode passthrough |
| `TestParameterEfficiency` | Trainable params reduction, IA3 most efficient, LoRA scales with rank |
| `TestPEFTConfig` | PEFT configuration options |

## Test Structure

```
tests/unit/peft/
    __init__.py
    test_peft.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/peft/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/peft/ --cov=src/codomyrmex/peft -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../peft/README.md)
- [All Tests](../README.md)
