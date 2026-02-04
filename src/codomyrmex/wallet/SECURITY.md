# Security Policy for Wallet Module

This document outlines security procedures and policies for the Wallet module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email security@codomyrmex.dev with the subject line: "SECURITY Vulnerability Report: Wallet - [Brief Description]".

Please include:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt within 2-3 business days.

## Security Architecture

### Key Storage

- Private keys are stored via `encryption.KeyManager` on the local filesystem.
- Key files use restrictive permissions (`0o600` - owner read/write only).
- Keys are stored in a designated directory, defaulting to a system temp directory.
- Key material is **never** logged, returned in API responses, or included in backups.

### Cryptographic Operations

- **Message Signing**: HMAC-SHA256 via Python's `hmac` module.
- **Signature Verification**: Uses `hmac.compare_digest()` for constant-time comparison, preventing timing attacks.
- **Recovery Hashing**: SHA-256 via Python's `hashlib` module for ritual response hashing.
- **Backup Integrity**: SHA-256 key hashes stored in backup records for verification.

### Recovery Security

- **Rate Limiting**: NaturalRitualRecovery enforces a maximum attempt count (default: 5) before lockout.
- **All-or-Nothing**: Failed recovery does not reveal which step failed to the caller.
- **Hash-Only Storage**: Ritual response secrets are stored as SHA-256 hashes only, never plaintext.

### Key Rotation

- `rotate_keys()` overwrites old key material with new random bytes.
- Rotation audit trail is maintained via `KeyRotation` class.
- Configurable rotation policies based on key age and signature count.

## Security Considerations

### Current Limitations (v0.1.0 Alpha)

1. **Mock Wallet IDs**: Wallet addresses are UUID-based, not derived from public keys.
2. **HMAC vs Digital Signatures**: Uses HMAC-SHA256 (symmetric) rather than asymmetric signatures (ECDSA/EdDSA). Suitable for single-agent use but not for external verification.
3. **In-Memory State**: Wallet-to-user mappings are stored in memory. Restart clears state.
4. **Key Derivation**: No HD wallet key derivation. Each wallet uses an independent random key.

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| Key exfiltration via backups | Backups contain only hashes, never raw keys |
| Timing attacks on signature verification | `hmac.compare_digest()` constant-time comparison |
| Brute-force recovery attempts | Attempt counter with configurable lockout threshold |
| Unauthorized key access | File permissions (0o600) on key storage |
| Key material in logs | Logger never receives raw key bytes |

## Best Practices for Using This Module

- Always use the latest stable version.
- Configure a dedicated, access-controlled directory for key storage (do not use default temp directory in production).
- Set appropriate `RotationPolicy` values based on your security requirements.
- Monitor rotation and recovery audit trails.
- Back up wallet metadata regularly and verify backup integrity.
- Use the `Wallet` facade for simplified operations that enforce safe patterns.

## Security Updates

Security patches will be documented in `CHANGELOG.md` and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This policy applies only to the `wallet` module within the Codomyrmex project.
