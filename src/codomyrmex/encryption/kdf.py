"""Key derivation functions.

Provides HKDF (HMAC-based Key Derivation Function) for deriving
cryptographic keys from shared secrets or other high-entropy material.
For password-based key derivation see ``Encryptor.derive_key()`` (PBKDF2).
"""


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_ALGORITHMS = {
    "sha256": hashes.SHA256,
    "sha384": hashes.SHA384,
    "sha512": hashes.SHA512,
}


def derive_key_hkdf(
    input_key_material: bytes | str,
    length: int = 32,
    salt: bytes | None = None,
    info: bytes | None = None,
    algorithm: str = "sha256",
) -> bytes:
    """Derive a cryptographic key using HKDF.

    HKDF is suitable for deriving keys from high-entropy inputs such as
    Diffie-Hellman shared secrets.  Do **not** use it for passwords;
    use ``Encryptor.derive_key()`` (PBKDF2) instead.

    Args:
        input_key_material: The source key material (str will be UTF-8 encoded)
        length: Desired output key length in bytes (default 32)
        salt: Optional salt (random bytes improve security)
        info: Optional context/application-specific info
        algorithm: Hash algorithm (sha256, sha384, sha512)

    Returns:
        Derived key of the requested length

    Raises:
        ValueError: If algorithm is not supported
    """
    if algorithm not in _ALGORITHMS:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. "
            f"Choose from: {', '.join(sorted(_ALGORITHMS))}"
        )
    if isinstance(input_key_material, str):
        input_key_material = input_key_material.encode("utf-8")

    hkdf = HKDF(
        algorithm=_ALGORITHMS[algorithm](),
        length=length,
        salt=salt,
        info=info,
        backend=default_backend(),
    )
    return hkdf.derive(input_key_material)
