# Codomyrmex Agents — src/codomyrmex/encryption

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Encryption module provides comprehensive cryptographic operations for securing data within the Codomyrmex ecosystem. It supports AES-256 symmetric encryption with CBC mode, RSA asymmetric encryption with OAEP padding, secure key generation and password-based key derivation using PBKDF2, digital signatures with PSS padding, file encryption utilities, and secure hashing functions.

## Active Components

### Core Infrastructure

- `encryptor.py` - Main encryption/decryption operations
  - Key Classes: `Encryptor`, `EncryptionError`
  - Key Functions: `encrypt()`, `decrypt()`, `generate_key()`, `derive_key()`, `sign()`, `verify()`
- `key_manager.py` - Secure key storage and retrieval
  - Key Classes: `KeyManager`
  - Key Functions: `store_key()`, `get_key()`, `delete_key()`
- `aes_gcm.py` - AES-GCM authenticated encryption
  - Key Classes: `AESGCMEncryptor`
- `container.py` - Secure data containers
  - Key Classes: `SecureDataContainer`

### Utility Functions

- `encrypt_data()` - Module-level encryption convenience function
- `decrypt_data()` - Module-level decryption convenience function
- `generate_aes_key()` - Generate random AES-256 keys
- `encrypt_file()` - File encryption utility
- `decrypt_file()` - File decryption utility
- `hash_data()` - Secure hashing (SHA-256, SHA-512, SHA-384, MD5)

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `Encryptor` | encryptor | Multi-algorithm encryption/decryption (AES, RSA) |
| `KeyManager` | key_manager | Secure key storage with file-based persistence |
| `AESGCMEncryptor` | aes_gcm | AES-GCM authenticated encryption |
| `SecureDataContainer` | container | Encrypted data container management |
| `EncryptionError` | encryptor | Exception for encryption failures |
| `encrypt()` | __init__ | Encrypt data with specified algorithm |
| `decrypt()` | __init__ | Decrypt data with specified algorithm |
| `generate_key()` | __init__ | Generate encryption keys |
| `derive_key()` | encryptor | PBKDF2-based key derivation from passwords |
| `sign()` | encryptor | Create RSA-PSS digital signatures |
| `verify()` | encryptor | Verify RSA-PSS digital signatures |
| `encrypt_file()` | __init__ | Encrypt files in place |
| `decrypt_file()` | __init__ | Decrypt encrypted files |
| `hash_data()` | __init__ | Compute cryptographic hashes |
| `generate_key_pair()` | encryptor | Generate RSA public/private key pairs |
| `generate_salt()` | encryptor | Generate cryptographically secure random salt |

## Operating Contracts

1. **Logging**: All operations use `logging_monitoring` for structured logging
2. **Error Handling**: Operations raise `EncryptionError` for consistent error handling
3. **Key Security**: Keys are stored with restrictive permissions (0o600)
4. **Algorithm Defaults**: AES-256 for symmetric, RSA-2048 for asymmetric operations
5. **Dependencies**: Requires `cryptography` package for cryptographic primitives

## Integration Points

- **logging_monitoring** - Structured logging for all operations
- **exceptions** - Base exception classes (`CodomyrmexError`)
- **auth** - Token and credential encryption support

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| auth | [../auth/AGENTS.md](../auth/AGENTS.md) | Authentication and authorization |
| compression | [../compression/AGENTS.md](../compression/AGENTS.md) | Data compression utilities |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security analysis and scanning |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
