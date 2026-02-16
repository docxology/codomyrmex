# Crypto Module — Security Considerations

**Version**: v0.1.0 | **Last Updated**: February 2026

## Key Generation

- All cryptographic keys are generated using CSPRNGs (`os.urandom()` backed by the operating system entropy pool).
- No keys are derived from predictable sources (timestamps, PIDs, sequential counters).
- Key sizes meet or exceed NIST recommendations for 128-bit security level.

## No Hardcoded Secrets

- No secret keys, passwords, seeds, or mnemonics are hardcoded in source code.
- Test fixtures use `os.urandom()` for key generation (see `conftest.py`).
- Example code in documentation uses placeholder values that are clearly marked as examples.

## Algorithm Selection

### Recommended

| Category | Algorithm | Rationale |
|---|---|---|
| Symmetric encryption | AES-256-GCM | NIST standard, authenticated encryption |
| Alternative symmetric | ChaCha20-Poly1305 | Constant-time, no AES-NI dependency |
| Asymmetric encryption | RSA-4096 with OAEP | Well-studied, large security margin |
| Digital signatures | Ed25519 | Fast, deterministic, no nonce reuse risk |
| Hashing | SHA-256 or SHA-3-256 | NIST standard |
| High-performance hash | BLAKE2b | Faster than SHA-2, NIST-recognized |
| Password hashing | Argon2id | OWASP recommended, memory-hard |
| Key exchange | X25519 (ECDH) | Fast, secure, constant-time |

### Deprecated

| Algorithm | Status | Reason |
|---|---|---|
| MD5 | **Deprecated** | Collision attacks demonstrated (2004). Included only for legacy checksum verification. |

### Excluded

| Algorithm | Reason |
|---|---|
| SHA-1 | Collision attacks demonstrated (SHAttered, 2017). Not included in the module. |
| DES / 3DES | Insufficient key size. Block size vulnerabilities (Sweet32). |
| RC4 | Statistical biases. Prohibited by RFC 7465. |
| ECB mode | No semantic security. Patterns visible in ciphertext. |

## Side-Channel Considerations

- **Constant-time comparisons**: All MAC and hash verification functions use `hmac.compare_digest()` for constant-time comparison, preventing timing attacks.
- **Nonce handling**: AES-GCM and ChaCha20-Poly1305 generate random nonces per encryption. Nonce reuse is catastrophic for GCM security; the API design prevents reuse by generating fresh nonces internally.
- **Key zeroing**: While Python's garbage collector does not guarantee immediate memory clearing, sensitive key material is not retained in module-level state. Users requiring stronger memory protections should consider hardware security modules.
- **Ed25519 deterministic nonces**: Ed25519 signatures use deterministic nonce generation (RFC 8032), eliminating the class of vulnerabilities caused by weak random nonce generation in ECDSA.

## Password Hashing

Argon2id is the recommended password hashing algorithm with the following default parameters (per OWASP 2024):

| Parameter | Value | Rationale |
|---|---|---|
| Time cost | 3 iterations | Balances security and performance |
| Memory cost | 65,536 KB (64 MB) | Memory-hard, resists GPU attacks |
| Parallelism | 4 threads | Matches typical server core count |
| Output length | 32 bytes | 256-bit derived key |

These parameters should be tuned for deployment environments. The module provides scrypt and PBKDF2 as alternatives for environments where Argon2 is not available.

## Certificate Handling

- Self-signed certificates are generated with proper Subject Alternative Names (SANs).
- Certificate chain verification uses the `cryptography` library's built-in chain validation.
- Default certificate validity is 365 days. Production deployments should use shorter validity periods with automated renewal.

## Cryptocurrency Security

- BIP-39 mnemonics use 256-bit entropy (24 words) by default.
- HD wallet derivation follows BIP-32/44 standards with hardened derivation for account-level keys.
- Transaction signing uses deterministic signatures (RFC 6979) where applicable.
- Address generation includes checksum verification to prevent transcription errors.

## Steganography Detection

- LSB embedding modifies the least significant bits of pixel values, which is detectable by statistical analysis.
- The `detection` submodule provides chi-squared analysis for detecting LSB steganography.
- Steganography should not be relied upon as a sole security mechanism; it provides obscurity, not cryptographic security.

## Randomness Quality

- The `random/nist_tests` submodule implements NIST SP 800-22 statistical tests for validating CSPRNG output.
- These tests should be run periodically in production to verify the health of the entropy source.
- The module does not implement its own PRNG; it delegates to `os.urandom()` and the operating system's CSPRNG.

## Threat Model

The crypto module assumes:

1. **Trusted execution environment**: The code runs on a machine controlled by the operator.
2. **Untrusted network**: All cryptographic protocols assume an active network adversary.
3. **No hardware security module**: Keys are stored in software. HSM integration is out of scope for v0.1.0.
4. **Standard attacker model**: Computational security against polynomial-time adversaries with access to modern hardware.

## Reporting Vulnerabilities

Security vulnerabilities in the crypto module should be reported through the Codomyrmex project's security disclosure process. Do not file public issues for security vulnerabilities.
