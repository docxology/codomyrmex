# Codomyrmex Agents — src/codomyrmex/encryption

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Encryption Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Encryption module providing encryption/decryption utilities and key management for the Codomyrmex platform. This module integrates with `security` and `config_management` modules to provide secure data encryption and key storage.

The encryption module serves as the encryption layer, providing algorithm-agnostic encryption interfaces with support for symmetric and asymmetric encryption algorithms.

## Module Overview

### Key Capabilities
- **Data Encryption**: Encrypt data using various algorithms
- **Data Decryption**: Decrypt data using various algorithms
- **Key Management**: Generate, store, and retrieve encryption keys
- **Key Derivation**: Derive keys from passwords securely
- **Digital Signing**: Create and verify digital signatures

### Key Features
- Algorithm-agnostic encryption interface
- Support for symmetric and asymmetric encryption
- Secure key management and storage
- Password-based key derivation
- Digital signature support

## Function Signatures

### Encryption Functions

```python
def encrypt(data: bytes, key: bytes) -> bytes
```

Encrypt data using the configured algorithm.

**Parameters:**
- `data` (bytes): Data to encrypt
- `key` (bytes): Encryption key

**Returns:** `bytes` - Encrypted data

**Raises:**
- `EncryptionError`: If encryption fails

```python
def decrypt(data: bytes, key: bytes) -> bytes
```

Decrypt data using the configured algorithm.

**Parameters:**
- `data` (bytes): Encrypted data
- `key` (bytes): Decryption key

**Returns:** `bytes` - Decrypted data

**Raises:**
- `EncryptionError`: If decryption fails

### Key Management Functions

```python
def generate_key() -> bytes
```

Generate a new encryption key.

**Returns:** `bytes` - Generated key

```python
def derive_key(password: str, salt: bytes) -> bytes
```

Derive an encryption key from a password.

**Parameters:**
- `password` (str): Password to derive key from
- `salt` (bytes): Salt for key derivation

**Returns:** `bytes` - Derived key

```python
def store_key(key_id: str, key: bytes) -> bool
```

Store an encryption key securely.

**Parameters:**
- `key_id` (str): Key identifier
- `key` (bytes): Key to store

**Returns:** `bool` - True if successful

```python
def get_key(key_id: str) -> Optional[bytes]
```

Retrieve a stored encryption key.

**Parameters:**
- `key_id` (str): Key identifier

**Returns:** `Optional[bytes]` - Stored key if found, None otherwise

### Digital Signature Functions

```python
def sign(data: bytes, private_key: bytes) -> bytes
```

Create a digital signature for data.

**Parameters:**
- `data` (bytes): Data to sign
- `private_key` (bytes): Private key for signing

**Returns:** `bytes` - Digital signature

```python
def verify(data: bytes, signature: bytes, public_key: bytes) -> bool
```

Verify a digital signature.

**Parameters:**
- `data` (bytes): Original data
- `signature` (bytes): Digital signature
- `public_key` (bytes): Public key for verification

**Returns:** `bool` - True if signature is valid

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `encryptor.py` – Base encryptor interface
- `key_manager.py` – Key management and storage
- `algorithms/` – Algorithm-specific implementations
  - `aes_encryptor.py` – AES encryption
  - `rsa_encryptor.py` – RSA encryption

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification
- `SECURITY.md` – Security considerations and best practices

## Operating Contracts

### Universal Encryption Protocols

All encryption operations within the Codomyrmex platform must:

1. **Security First** - All encryption operations must use secure algorithms
2. **Key Protection** - Keys must be stored securely and never exposed
3. **Error Handling** - Encryption failures must not leak sensitive information
4. **Audit Logging** - All encryption operations must be logged (without keys)
5. **Algorithm Validation** - Only approved encryption algorithms may be used

### Integration Guidelines

When integrating with other modules:

1. **Use Security Module** - Integrate with security module for threat detection
2. **Secret Management** - Store keys via config_management module
3. **Document Encryption** - Support document encryption for sensitive data
4. **Secure Storage** - Use secure storage for key management

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **Security Guide**: [../../../SECURITY.md](../../../SECURITY.md) - Security best practices (root)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [security](../security/AGENTS.md) - Security scanning
    - [config_management](../config_management/AGENTS.md) - Secret management

