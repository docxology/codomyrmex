"""Backward-compatibility shim -- redirects to ``encryption.keys.kdf``."""

from .keys.kdf import *  # noqa: F401,F403
from .keys.kdf import derive_key_hkdf
