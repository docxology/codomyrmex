"""Skip markers for tests that rely on POSIX file-permission enforcement."""

from __future__ import annotations

import os
import sys

import pytest

#: True when the test process can bypass file mode bits (POSIX superuser).
RUNNING_AS_ROOT = hasattr(os, "geteuid") and os.geteuid() == 0

#: Tests that provoke errors by ``chmod``-ing files/directories unreadable or
#: read-only. A superuser ignores those mode bits, and Windows does not apply
#: POSIX modes to directories, so the provoked error never happens there.
requires_permission_enforcement = pytest.mark.skipif(
    RUNNING_AS_ROOT or sys.platform == "win32",
    reason="needs POSIX permission enforcement (not root, not Windows)",
)
