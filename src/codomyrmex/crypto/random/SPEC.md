# Crypto Random -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Cryptographically secure random number generation (CSPRNG) and NIST SP 800-22 statistical randomness tests. The `generator` submodule provides production-grade random value generation; the `testing` submodule validates randomness quality.

## Architecture

```
crypto/random/
├── __init__.py    # 10 re-exports across 2 submodules
├── generator.py   # CSPRNG: bytes, integers, strings, nonces, UUIDs
└── testing.py     # NIST SP 800-22 statistical test suite
```

## Key Classes and Functions

### generator.py

| Name | Kind | Signature | Description |
|------|------|-----------|-------------|
| `secure_random_bytes` | function | `(length: int) -> bytes` | Generate cryptographically secure random bytes |
| `secure_random_int` | function | `(min_val: int, max_val: int) -> int` | Generate a secure random integer in [min_val, max_val] |
| `secure_random_string` | function | `(length: int, charset: str = ...) -> str` | Generate a secure random string from the given character set |
| `generate_nonce` | function | `(length: int = 16) -> bytes` | Generate a unique nonce suitable for cryptographic protocols |
| `generate_uuid4` | function | `() -> str` | Generate a cryptographically random UUID v4 |

### testing.py

| Name | Kind | Signature | Description |
|------|------|-----------|-------------|
| `NistTestResult` | dataclass | `test_name: str, p_value: float, passed: bool` | Result of a single NIST statistical test |
| `monobit_test` | function | `(data: bytes) -> NistTestResult` | NIST frequency (monobit) test |
| `block_frequency_test` | function | `(data: bytes, block_size: int = 128) -> NistTestResult` | NIST block frequency test |
| `runs_test` | function | `(data: bytes) -> NistTestResult` | NIST runs test for randomness |
| `run_nist_suite` | function | `(data: bytes) -> list[NistTestResult]` | Run all implemented NIST tests and return results |

## Dependencies

- Python `os` (`os.urandom`), `secrets`, `uuid` (standard library)
- No external dependencies

## Constraints

- `secure_random_bytes` length must be >= 1.
- `secure_random_int` requires min_val <= max_val.
- NIST tests require at least 128 bytes of input data for meaningful results.
- All generators use `os.urandom` / `secrets` module as the entropy source.

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Invalid length (< 1), min_val > max_val, insufficient data for NIST tests |

## Navigation

- **Parent**: [crypto/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
