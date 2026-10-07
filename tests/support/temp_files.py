"""Temporary file paths for tests that need a real path outside ``tmp_path``.

``tempfile.NamedTemporaryFile(delete=False).name`` leaves the file object open
until garbage collection; ``mkstemp`` returns a descriptor that is closed here
at once. Callers own the file and should remove it when done.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def temp_file_path(suffix: str = "") -> Path:
    """Create an empty temporary file and return its path (no open handle)."""
    fd, name = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return Path(name)
