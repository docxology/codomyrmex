# encryption/core Personal AI Infrastructure

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## AI Capabilities

This module exposes the following capabilities for AI agent use:

- **Symmetric encryption/decryption** -- Encrypt and decrypt arbitrary byte data or strings using AES-256-CBC with a 32-byte key via `encrypt_data()` / `decrypt_data()` or `Encryptor.encrypt()` / `Encryptor.decrypt()`
- **Asymmetric encryption/decryption** -- Encrypt small payloads with RSA-OAEP (2048-bit) using `Encryptor(algorithm="RSA")`
- **Key generation** -- Generate random AES-256 keys with `generate_aes_key()`, RSA keypairs with `Encryptor.generate_key_pair()`, or password-derived keys with `Encryptor.derive_key()`
- **Digital signatures** -- Sign data with RSA-PSS via `Encryptor.sign()` and verify with `Encryptor.verify()`
- **File encryption** -- Encrypt/decrypt files on disk with `Encryptor.encrypt_file()` / `Encryptor.decrypt_file()`
- **Hashing** -- Compute SHA-256/SHA-512/SHA-384/MD5 hex digests with `Encryptor.hash_data()`
- **Salt generation** -- Generate cryptographically secure random salt with `Encryptor.generate_salt()`

## Usage Notes for Agents

- For new code, prefer `encryption.algorithms.AESGCMEncryptor` over AES-CBC (this module).
- All errors raise `EncryptionError`; agents should handle this exception.
- RSA encryption is limited to small payloads (< ~190 bytes for 2048-bit keys with OAEP).
