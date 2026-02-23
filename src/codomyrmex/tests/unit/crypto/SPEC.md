# Crypto Module — Test Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Coverage Targets

| Submodule | Target Coverage | Priority |
|---|---|---|
| graphy/symmetric | >= 95% | Critical |
| graphy/asymmetric | >= 90% | Critical |
| graphy/hashing | >= 95% | Critical |
| graphy/signatures | >= 95% | Critical |
| graphy/kdf | >= 90% | High |
| graphy/mac | >= 90% | High |
| graphy/certificates | >= 85% | Medium |
| currency/wallets | >= 85% | High |
| currency/blockchain | >= 90% | High |
| currency/transactions | >= 85% | Medium |
| currency/addresses | >= 90% | High |
| currency/tokens | >= 80% | Medium |
| analysis/entropy | >= 95% | High |
| analysis/frequency | >= 85% | Medium |
| analysis/strength | >= 85% | Medium |
| analysis/classical_breaking | >= 80% | Low |
| steganography/image_lsb | >= 85% | Medium |
| steganography/text_steg | >= 90% | Medium |
| steganography/detection | >= 80% | Low |
| encoding/base_encodings | >= 95% | High |
| encoding/pem | >= 90% | High |
| random/csprng | >= 90% | Critical |
| random/nist_tests | >= 85% | High |
| protocols/key_exchange | >= 90% | Critical |
| protocols/secret_sharing | >= 90% | High |
| protocols/zero_knowledge | >= 85% | Medium |

**Overall target**: >= 90% line coverage across the crypto module.

## Test Categories

### Correctness Tests

- **Round-trip**: Encrypt then decrypt recovers original plaintext for all cipher modes.
- **Known-answer**: Compare outputs against published test vectors (NIST CAVP, RFC test vectors).
- **Deterministic**: Same inputs produce same outputs for deterministic algorithms (hashing, Ed25519 signatures).
- **Edge cases**: Empty input, maximum-size input, single-byte input.

### Error Handling Tests

- **Invalid key size**: Verify appropriate exceptions for wrong key lengths.
- **Corrupted ciphertext**: Verify decryption fails with clear error on tampered data.
- **Invalid signatures**: Verify signature verification returns False (not exception) for invalid signatures.
- **Malformed input**: Verify encoding/decoding rejects malformed input with `EncodingError`.

### Security Tests

- **Nonce uniqueness**: Verify nonces are unique across multiple encryptions (statistical test).
- **Key randomness**: Verify generated keys pass NIST frequency test.
- **Constant-time verification**: Verify MAC/hash comparison does not leak timing information (best-effort test).
- **Authentication tag verification**: Verify GCM/Poly1305 reject modified ciphertext.

### Performance Tests (marked `@pytest.mark.slow`)

- **Throughput**: Measure encryption/decryption speed for 1MB, 10MB, 100MB payloads.
- **Key generation**: Measure time for RSA-4096, Ed25519, X25519 key generation.
- **KDF**: Measure Argon2id derivation time with default parameters.

### Integration Tests

- **Cross-submodule**: Generate key (graphy) -> sign (graphy) -> verify (graphy) -> encode (encoding).
- **Wallet workflow**: Generate mnemonic (currency) -> derive key (currency) -> generate address (currency) -> sign transaction (currency).
- **Protocol workflow**: Exchange keys (protocols) -> derive shared secret -> encrypt (graphy) -> decrypt (graphy).

## Test Vector Sources

| Algorithm | Source |
|---|---|
| AES-GCM | NIST SP 800-38D test vectors |
| SHA-256 | NIST CAVP SHA test vectors |
| SHA-3 | NIST CAVP SHA-3 test vectors |
| HMAC-SHA256 | RFC 4231 test vectors |
| PBKDF2 | RFC 6070 test vectors |
| Ed25519 | RFC 8032 test vectors |
| X25519 | RFC 7748 test vectors |
| Base64 | RFC 4648 test vectors |
| Base58 | Bitcoin reference implementation vectors |

## Failure Criteria

A test run fails if:
1. Any correctness test fails.
2. Any security test fails.
3. Coverage drops below the target for any critical-priority submodule.
4. Performance tests exceed 2x the baseline time (regression detection).
