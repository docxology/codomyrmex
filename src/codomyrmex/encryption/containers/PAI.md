# encryption/containers Personal AI Infrastructure

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## AI Capabilities

This module exposes the following capabilities for AI agent use:

- **Encrypt structured data** -- Serialize any JSON-serializable Python object with optional metadata and encrypt it using AES-GCM via `SecureDataContainer.pack(data, metadata)`
- **Decrypt structured data** -- Decrypt and deserialize an encrypted payload back to a Python dict with `"data"` and `"metadata"` keys via `SecureDataContainer.unpack(encrypted_data)`
- **Tamper detection** -- Automatically detects ciphertext tampering during `unpack()` (raises `InvalidTag`)
- **Metadata attachment** -- Attach arbitrary key-value metadata that is encrypted alongside the primary data

## Usage Notes for Agents

- Data must be JSON-serializable (dicts, lists, strings, numbers, booleans, None).
- The container uses AES-GCM internally; no need to manage nonces or tags.
- For key management, use `encryption.keys.KeyManager` to store/retrieve the container key.
- The `unpack()` return value is always `{"data": ..., "metadata": {...}}`.
