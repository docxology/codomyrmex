# DEPRECATED(v0.2.0): Shim module. Import from encryption.keys.key_manager instead. Will be removed in v0.3.0.
"""Backward-compatibility shim -- redirects to ``encryption.keys.key_manager``."""

from .keys.key_manager import *  # noqa: F401,F403
from .keys.key_manager import KeyManager
