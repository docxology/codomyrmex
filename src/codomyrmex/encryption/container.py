"""Backward-compatibility shim -- redirects to ``encryption.containers.container``."""

from .containers.container import *  # noqa: F401,F403
from .containers.container import SecureDataContainer
