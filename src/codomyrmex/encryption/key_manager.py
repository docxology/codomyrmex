"""Backward-compatibility shim -- redirects to ``encryption.keys.key_manager``."""

from .keys.key_manager import *  # noqa: F401,F403
from .keys.key_manager import KeyManager
