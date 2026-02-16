"""Key management, derivation, and authentication utilities.

Provides:
- ``KeyManager`` -- secure storage and retrieval of encryption keys
- ``derive_key_hkdf`` -- HKDF-based key derivation from high-entropy input
- ``compute_hmac`` / ``verify_hmac`` -- HMAC computation and constant-time
  verification
"""

from .hmac_utils import compute_hmac, verify_hmac
from .kdf import derive_key_hkdf
from .key_manager import KeyManager

__all__ = [
    "KeyManager",
    "compute_hmac",
    "derive_key_hkdf",
    "verify_hmac",
]
