# Codomyrmex Agents — src/codomyrmex/encryption

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Encryption/decryption utilities and key management. Provides algorithm-agnostic encryption interface with support for AES and RSA algorithms, key derivation, digital signatures, and secure key storage.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `encryptor.py` – Encryption/decryption implementation
- `key_manager.py` – Key storage and retrieval manager

## Key Classes and Functions

### Encryptor (`encryptor.py`)
- `Encryptor(algorithm: str = "AES")` – Initialize encryptor with specified algorithm (AES, RSA)
- `encrypt(data: bytes, key: bytes) -> bytes` – Encrypt data using the configured algorithm
- `decrypt(data: bytes, key: bytes) -> bytes` – Decrypt data using the configured algorithm
- `generate_key() -> bytes` – Generate a new encryption key
- `derive_key(password: str, salt: bytes) -> bytes` – Derive an encryption key from a password using PBKDF2
- `sign(data: bytes, private_key: bytes) -> bytes` – Create a digital signature for data
- `verify(data: bytes, signature: bytes, public_key: bytes) -> bool` – Verify a digital signature
- `_encrypt_aes(data: bytes, key: bytes) -> bytes` – Internal AES encryption (CBC mode with PKCS7 padding)
- `_decrypt_aes(data: bytes, key: bytes) -> bytes` – Internal AES decryption
- `_encrypt_rsa(data: bytes, key: bytes) -> bytes` – Internal RSA encryption (OAEP padding)
- `_decrypt_rsa(data: bytes, key: bytes) -> bytes` – Internal RSA decryption

### KeyManager (`key_manager.py`)
- `KeyManager(key_dir: Optional[Path] = None)` – Initialize key manager with storage directory
- `store_key(key_id: str, key: bytes) -> bool` – Store an encryption key securely (with restrictive permissions)
- `get_key(key_id: str) -> Optional[bytes]` – Retrieve a stored encryption key
- `delete_key(key_id: str) -> bool` – Delete a stored encryption key

### Module Functions (`__init__.py`)
- `encrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` – Encrypt data
- `decrypt(data: bytes, key: bytes, algorithm: str = "AES") -> bytes` – Decrypt data
- `generate_key(algorithm: str = "AES") -> bytes` – Generate a new encryption key
- `get_encryptor(algorithm: str = "AES") -> Encryptor` – Get an encryptor instance

### Exceptions
- `EncryptionError` – Raised when encryption operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation