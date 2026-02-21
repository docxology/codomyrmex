# DEPRECATED(v0.2.0): Shim module. Import from wallet.security.backup instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: wallet.security.backup"""
from .security.backup import *  # noqa: F401,F403
from .security.backup import BackupManager
