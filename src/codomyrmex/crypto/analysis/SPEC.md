# Crypto Analysis -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Cryptanalysis utilities for evaluating entropy, statistical properties, password/key strength, frequency distributions, and classical cipher identification. Organized into four submodules: `entropy`, `frequency`, `strength`, and `classical`.

## Architecture

```
crypto/analysis/
├── __init__.py       # 23 re-exports across 4 submodules
├── entropy.py        # Shannon entropy, byte entropy, chi-squared, serial correlation
├── frequency.py      # Character/bigram frequency, index of coincidence
├── strength.py       # Password/key strength assessment, crack-time estimation
└── classical.py      # Caesar/Vigenere encrypt, decrypt, and breaking
```

## Key Classes and Functions

### entropy.py

| Name | Kind | Signature | Description |
|------|------|-----------|-------------|
| `ChiSquaredResult` | dataclass | `chi_squared: float, p_value: float, degrees_of_freedom: int, is_random: bool` | Result container for chi-squared randomness test |
| `shannon_entropy` | function | `(data: bytes) -> float` | Shannon entropy in bits per byte (0.0--8.0) |
| `byte_entropy` | function | `(data: bytes) -> float` | Normalized byte-level entropy (0.0--1.0) |
| `chi_squared_test` | function | `(data: bytes, confidence: float = 0.95) -> ChiSquaredResult` | Chi-squared test for uniform byte distribution |
| `serial_correlation` | function | `(data: bytes) -> float` | Serial correlation coefficient between adjacent bytes |

### strength.py

| Name | Kind | Signature | Description |
|------|------|-----------|-------------|
| `StrengthResult` | dataclass | `score: float, level: str, entropy_bits: float, suggestions: list[str], crack_time: str` | Strength assessment result container |
| `assess_password_strength` | function | `(password: str) -> StrengthResult` | Evaluate password strength with entropy and crack-time |
| `estimate_crack_time` | function | `(entropy_bits: float, guesses_per_second: float = 1e9) -> str` | Estimate brute-force crack time from entropy bits |
| `assess_key_strength` | function | `(key: bytes, algorithm: str = "aes") -> StrengthResult` | Evaluate cryptographic key strength for a given algorithm |
| `check_common_passwords` | function | `(password: str) -> bool` | Check if password appears in common password lists |

### frequency.py

| Name | Kind | Description |
|------|------|-------------|
| `character_frequency` | function | Character frequency distribution for text data |
| `bigram_frequency` | function | Bigram frequency distribution |
| `index_of_coincidence` | function | Index of Coincidence for cipher analysis |
| `expected_english_frequency` | function | Expected English letter frequency reference |

### classical.py

| Name | Kind | Description |
|------|------|-------------|
| `CaesarResult` | dataclass | Result of Caesar cipher breaking (shift, plaintext, score) |
| `VigenereResult` | dataclass | Result of Vigenere cipher breaking (key, plaintext, score) |
| `caesar_encrypt` | function | Encrypt plaintext with Caesar cipher |
| `caesar_decrypt` | function | Decrypt ciphertext with known Caesar shift |
| `break_caesar` | function | Break Caesar cipher via frequency analysis |
| `vigenere_encrypt` | function | Encrypt plaintext with Vigenere cipher |
| `vigenere_decrypt` | function | Decrypt ciphertext with known Vigenere key |
| `break_vigenere` | function | Break Vigenere cipher via Kasiski examination |
| `detect_cipher_type` | function | Identify probable classical cipher type from ciphertext |

## Dependencies

- Python `math`, `collections`, `statistics` (standard library only)
- No external cryptographic library dependencies

## Constraints

- Entropy functions require non-empty `bytes` input.
- `chi_squared_test` confidence parameter must be in (0, 1).
- Strength scores are normalized to 0.0--1.0 range.

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Empty data input, invalid confidence range |
| `TypeError` | Wrong input type (e.g., `str` instead of `bytes` for entropy functions) |

## Navigation

- **Parent**: [crypto/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
