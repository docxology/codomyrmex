# DEPRECATED(v0.2.0): Shim module. Import from encryption.containers.container instead. Will be removed in v0.3.0.
"""Backward-compatibility shim -- redirects to ``encryption.containers.container``."""

from .containers.container import *  # noqa: F401,F403
from .containers.container import SecureDataContainer
