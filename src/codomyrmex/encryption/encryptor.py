# DEPRECATED(v0.2.0): Shim module. Import from encryption.core.encryptor instead. Will be removed in v0.3.0.
"""Backward-compatibility shim -- redirects to ``encryption.core.encryptor``."""

from .core.encryptor import *  # noqa: F401,F403
from .core.encryptor import Encryptor, decrypt_data, encrypt_data, generate_aes_key
