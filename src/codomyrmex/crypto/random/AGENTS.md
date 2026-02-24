# crypto/random -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `crypto/random` submodule provides cryptographically secure random number generation and NIST SP 800-22 statistical randomness tests. The generator side produces random bytes, integers, strings, nonces, and UUIDs. The testing side validates randomness quality using monobit, runs, and block frequency tests.

## When to Use This Module

- You need cryptographically secure random bytes, integers, or strings (passwords, tokens)
- You need random nonces for cryptographic operations
- You need to generate UUIDv4 identifiers
- You need to verify the statistical quality of random data (NIST SP 800-22 suite)
- You are auditing or testing a CSPRNG implementation

## Exports

| Name | Kind | Purpose |
|------|------|---------|
| `secure_random_bytes` | function | Generate N bytes from CSPRNG |
| `secure_random_int` | function | Generate random integer in a range |
| `secure_random_string` | function | Generate random alphanumeric string of given length |
| `generate_nonce` | function | Generate a random nonce (default 12 or 16 bytes) |
| `generate_uuid4` | function | Generate a random UUIDv4 string |
| `NistTestResult` | dataclass | Result container for NIST statistical tests |
| `monobit_test` | function | NIST monobit (frequency) test for randomness |
| `runs_test` | function | NIST runs test for randomness |
| `block_frequency_test` | function | NIST block frequency test |
| `run_nist_suite` | function | Run all NIST tests and return aggregate results |

## Example Agent Usage

```python
from codomyrmex.crypto.random import (
    secure_random_bytes, secure_random_string, generate_nonce, run_nist_suite,
)

# Generate cryptographic material
key_bytes = secure_random_bytes(32)
nonce = generate_nonce(12)
api_token = secure_random_string(48)

# Validate randomness quality
data = secure_random_bytes(1000)
results = run_nist_suite(data)
for r in results:
    print(r.test_name, r.passed, r.p_value)
```

## Constraints

- All random generation uses `os.urandom` or equivalent CSPRNG; never pseudo-random.
- NIST tests require sufficient data length (typically 100+ bytes) for meaningful results.
- `secure_random_int` uses rejection sampling for uniform distribution.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `crypto.analysis` | Entropy functions complement NIST randomness tests |
| `crypto.graphy` | Symmetric key generation uses similar CSPRNG primitives |
| `encryption.algorithms` | AES-GCM nonce generation can be replaced with `generate_nonce` |
