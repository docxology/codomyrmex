"""Backward-compatibility shim -- redirects to ``encryption.algorithms.aes_gcm``."""

from .algorithms.aes_gcm import *  # noqa: F401,F403
from .algorithms.aes_gcm import AESGCMEncryptor
