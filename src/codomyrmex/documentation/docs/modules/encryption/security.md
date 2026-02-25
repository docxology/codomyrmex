# Security Policy for Encryption Module

This document outlines security procedures and policies for the Encryption module.

## Reporting a Vulnerability

If you discover a security vulnerability within this module, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email security@codomyrmex.dev with the subject line: "SECURITY Vulnerability Report: Encryption Module - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the module affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Security patches and updates for this module will be documented in the module changelog and released as part of regular version updates. Critical vulnerabilities may warrant out-of-band releases.

## Scope

This security policy applies only to the `Encryption` module within the Codomyrmex project. For project-wide security concerns, please refer to the main project's security policy or contact the core project maintainers.

## Security Considerations for Encryption Module

### Cryptographic Algorithms

- **AES-256-CBC**: Symmetric encryption using 256-bit keys with CBC mode and PKCS7 padding.
- **AES-256-GCM**: Authenticated encryption providing both confidentiality and integrity.
- **RSA-OAEP**: Asymmetric encryption using 2048-bit keys with OAEP padding and SHA-256.
- **Digital Signatures**: RSA-PSS with SHA-256 for data integrity verification.

### Key Management Security

- **Key Generation**: Uses `os.urandom()` for cryptographically secure random key generation.
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations for password-based key derivation.
- **Key Storage**: Keys should never be stored in plaintext; use secure key vaults or hardware security modules (HSM).

### Common Vulnerabilities Mitigated

1. **Weak Key Generation**: Uses CSPRNG (Cryptographically Secure Pseudo-Random Number Generator).
2. **IV/Nonce Reuse**: Fresh IV generated for each encryption operation.
3. **Padding Oracle Attacks**: Proper exception handling prevents timing-based attacks.
4. **Key Exposure**: Keys are not logged or serialized in error messages.

### Cryptographic Best Practices

- Never use MD5 or SHA-1 for security-sensitive operations.
- Always use authenticated encryption (AES-GCM) when possible.
- Ensure proper key rotation policies are in place.
- Use constant-time comparison for sensitive comparisons.

## Best Practices for Using This Module

- Always use the latest stable version of the module.
- Store encryption keys securely (environment variables, secrets manager, HSM).
- Never hardcode encryption keys in source code.
- Use unique salts for each password derivation operation.
- Implement proper key rotation procedures.
- Use AES-GCM for authenticated encryption when data integrity is required.
- Verify signatures before trusting signed data.
- Securely wipe sensitive data from memory when no longer needed.
- Follow the principle of least privilege when configuring access or permissions.
- Regularly review configurations and logs for suspicious activity.

## Secure Configuration

```python
# Example secure configuration
from codomyrmex.encryption import Encryptor, generate_aes_key

# Generate a secure key (store this securely!)
key = generate_aes_key()

# Use AES for symmetric encryption
encryptor = Encryptor(algorithm="AES")

# Encrypt sensitive data
ciphertext = encryptor.encrypt(b"sensitive data", key)

# For password-based encryption
salt = Encryptor.generate_salt()
derived_key = encryptor.derive_key("user_password", salt)

# For asymmetric encryption (RSA)
rsa_encryptor = Encryptor(algorithm="RSA")
private_key, public_key = rsa_encryptor.generate_key_pair()
```

## Security Audit Checklist

- [ ] Keys are stored securely (not in source code)
- [ ] Unique IVs/nonces are used for each encryption
- [ ] Salt values are stored alongside derived key hashes
- [ ] Error messages do not leak sensitive information
- [ ] Key rotation policy is documented and implemented
- [ ] Deprecated algorithms (MD5, SHA-1, DES, 3DES) are not used

Thank you for helping keep Codomyrmex and the Encryption module secure.
