# DEPRECATED(v0.2.0): Shim module. Import from encryption.keys.kdf instead. Will be removed in v0.3.0.
"""Backward-compatibility shim -- redirects to ``encryption.keys.kdf``."""

from .keys.kdf import *  # noqa: F401,F403
from .keys.kdf import derive_key_hkdf
