<!-- readme: generated -->

# encryption

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/encryption/`

## Overview

Encryption module for Codomyrmex.

Provides encryption, hashing, digital signatures, and key management:
- AES-256 symmetric encryption (CBC and GCM)
- RSA asymmetric encryption and digital signatures
- Key generation and key derivation (PBKDF2, HKDF)
- HMAC message authentication
- Secure hashing (SHA-256, SHA-384, SHA-512, MD5)
- Secure data containers for JSON objects
- Key management for secure key storage

## Public Exports

`encryption` exports 18 public symbols via `__all__`:

`AESGCMEncryptor`, `EncryptionError`, `Encryptor`, `KeyManager`, `SecureDataContainer`, `Signer`, `cli_commands`, `compute_hmac`, `decrypt`, `decrypt_file`, `derive_key_hkdf`, `encrypt`, `encrypt_file`, `generate_aes_key`, `generate_key`, `get_encryptor`, `hash_data`, `verify_hmac`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../encryption/](../../../../encryption/)
