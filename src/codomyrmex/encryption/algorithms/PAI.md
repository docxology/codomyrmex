# encryption/algorithms Personal AI Infrastructure

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## AI Capabilities

This module exposes the following capabilities for AI agent use:

- **Authenticated symmetric encryption** -- Encrypt data using AES-256-GCM with automatic nonce generation via `AESGCMEncryptor.encrypt(data)`, providing both confidentiality and integrity
- **Authenticated decryption with integrity check** -- Decrypt and verify ciphertext via `AESGCMEncryptor.decrypt(data)`, automatically detecting tampered data
- **Associated data (AAD) support** -- Authenticate additional metadata alongside encrypted content using the `associated_data` parameter (e.g., headers or routing info that must be verified but not encrypted)
- **Automatic key generation** -- Instantiate `AESGCMEncryptor()` with no arguments to auto-generate a 256-bit key
- **Key access** -- Read the `.key` attribute to persist or transfer the encryption key

## Usage Notes for Agents

- This is the recommended symmetric cipher for all new encryption tasks.
- Each `encrypt()` call generates a fresh nonce; the same key can safely encrypt many messages.
- Tampered ciphertext raises `cryptography.exceptions.InvalidTag` on decrypt.
- For key storage/management, use `encryption.keys.KeyManager`.
