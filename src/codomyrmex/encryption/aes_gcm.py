# DEPRECATED(v0.2.0): Shim module. Import from encryption.algorithms.aes_gcm instead. Will be removed in v0.3.0.
"""Backward-compatibility shim -- redirects to ``encryption.algorithms.aes_gcm``."""

from .algorithms.aes_gcm import *  # noqa: F401,F403
from .algorithms.aes_gcm import AESGCMEncryptor
