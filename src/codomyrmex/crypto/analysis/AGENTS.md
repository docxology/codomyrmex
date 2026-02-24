# crypto/analysis -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `crypto/analysis` submodule provides cryptanalysis tools: entropy measurement, frequency analysis, password/key strength assessment, and classical cipher operations (Caesar, Vigenere).

## When to Use This Module

- You need to measure the randomness or entropy of data (Shannon entropy, byte entropy, chi-squared, serial correlation)
- You need to analyze character or bigram frequency distributions in text
- You need to assess password or key strength, estimate crack times, or check against common passwords
- You need to encrypt/decrypt with classical ciphers (Caesar, Vigenere) or attempt to break them
- You need to detect what type of classical cipher was used on a ciphertext

## Exports

| Name | Kind | Purpose |
|------|------|---------|
| `shannon_entropy` | function | Compute Shannon entropy (bits per symbol) of a string |
| `byte_entropy` | function | Compute entropy of raw byte data |
| `chi_squared_test` | function | Chi-squared test for uniform distribution |
| `serial_correlation` | function | Serial correlation coefficient for byte sequences |
| `ChiSquaredResult` | dataclass | Result container for chi-squared test |
| `character_frequency` | function | Character frequency distribution of text |
| `bigram_frequency` | function | Bigram (2-char) frequency distribution |
| `index_of_coincidence` | function | Index of coincidence for cipher analysis |
| `expected_english_frequency` | function | Reference English letter frequency table |
| `assess_password_strength` | function | Score a password's strength |
| `assess_key_strength` | function | Score a cryptographic key's strength |
| `estimate_crack_time` | function | Estimate time to brute-force a password |
| `check_common_passwords` | function | Check if password is in common password list |
| `StrengthResult` | dataclass | Result container for strength assessments |
| `caesar_encrypt` / `caesar_decrypt` | function | Caesar cipher encrypt/decrypt |
| `vigenere_encrypt` / `vigenere_decrypt` | function | Vigenere cipher encrypt/decrypt |
| `break_caesar` / `break_vigenere` | function | Automated cipher breaking |
| `detect_cipher_type` | function | Detect whether ciphertext is Caesar, Vigenere, or other |
| `CaesarResult` / `VigenereResult` | dataclass | Results from cipher-breaking attempts |

## Example Agent Usage

```python
from codomyrmex.crypto.analysis import (
    shannon_entropy, assess_password_strength, break_caesar,
)

# Measure entropy
entropy = shannon_entropy("Hello World")

# Assess password
result = assess_password_strength("MyP@ssw0rd!")
print(result.score, result.crack_time)

# Break a Caesar cipher
ct = "Khoor Zruog"
result = break_caesar(ct)
print(result.plaintext, result.shift)
```

## Constraints

- Classical cipher operations are for educational/analysis purposes, not production security.
- `check_common_passwords` requires an internal password list; returns `False` for empty lists.
- Entropy functions work on both `str` and `bytes` inputs.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `crypto.random` | Generate random data to test with entropy functions |
| `crypto.graphy` | Production-grade cryptography (contrast with classical ciphers here) |
| `encryption.keys` | Key strength assessment complements key management |
