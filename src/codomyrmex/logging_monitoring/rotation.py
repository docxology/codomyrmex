"""Log rotation manager - Backward Compatibility Shim.

This module re-exports LogRotationManager from its new location in the
handlers subpackage. All existing import paths continue to work unchanged.

The canonical implementation now lives in:
    handlers/rotation.py

For new code, prefer:
    >>> from codomyrmex.logging_monitoring.handlers import LogRotationManager
"""

from .handlers.rotation import LogRotationManager  # noqa: F401
