"""Cryptography primitives: symmetric, asymmetric, hashing, signatures, KDF, MAC, certificates."""

from codomyrmex.crypto.graphy.asymmetric import (
    KeyPair,
    generate_ec_keypair,
    generate_ed25519_keypair,
    generate_rsa_keypair,
    generate_x25519_keypair,
    load_private_key,
    load_public_key,
    rsa_decrypt,
    rsa_encrypt,
    serialize_private_key,
    serialize_public_key,
)
from codomyrmex.crypto.graphy.certificates import (
    ValidationResult,
    export_certificate_pem,
    generate_csr,
    generate_self_signed_cert,
    load_certificate_pem,
    validate_certificate_chain,
)
from codomyrmex.crypto.graphy.hashing import (
    HashAlgorithm,
    hash_blake2b,
    hash_data,
    hash_md5,
    hash_sha256,
    hash_sha3_256,
    hash_sha512,
    verify_hash,
)
from codomyrmex.crypto.graphy.kdf import (
    DerivedKey,
    derive_argon2id,
    derive_hkdf,
    derive_pbkdf2,
    derive_scrypt,
)
from codomyrmex.crypto.graphy.mac import (
    compute_cmac,
    compute_hmac_sha256,
    compute_poly1305,
    verify_hmac_sha256,
)
from codomyrmex.crypto.graphy.signatures import (
    sign_ecdsa,
    sign_ed25519,
    sign_rsa_pss,
    verify_ecdsa,
    verify_ed25519,
    verify_rsa_pss,
)
from codomyrmex.crypto.graphy.symmetric import (
    CipherResult,
    decrypt_aes_gcm,
    decrypt_chacha20,
    encrypt_aes_gcm,
    encrypt_chacha20,
    generate_symmetric_key,
)

__all__ = [
    # symmetric
    "CipherResult",
    "decrypt_aes_gcm",
    "decrypt_chacha20",
    "encrypt_aes_gcm",
    "encrypt_chacha20",
    "generate_symmetric_key",
    # asymmetric
    "KeyPair",
    "generate_ec_keypair",
    "generate_ed25519_keypair",
    "generate_rsa_keypair",
    "generate_x25519_keypair",
    "load_private_key",
    "load_public_key",
    "rsa_decrypt",
    "rsa_encrypt",
    "serialize_private_key",
    "serialize_public_key",
    # hashing
    "HashAlgorithm",
    "hash_blake2b",
    "hash_data",
    "hash_md5",
    "hash_sha256",
    "hash_sha3_256",
    "hash_sha512",
    "verify_hash",
    # signatures
    "sign_ecdsa",
    "sign_ed25519",
    "sign_rsa_pss",
    "verify_ecdsa",
    "verify_ed25519",
    "verify_rsa_pss",
    # kdf
    "DerivedKey",
    "derive_argon2id",
    "derive_hkdf",
    "derive_pbkdf2",
    "derive_scrypt",
    # mac
    "compute_cmac",
    "compute_hmac_sha256",
    "compute_poly1305",
    "verify_hmac_sha256",
    # certificates
    "ValidationResult",
    "export_certificate_pem",
    "generate_csr",
    "generate_self_signed_cert",
    "load_certificate_pem",
    "validate_certificate_chain",
]
