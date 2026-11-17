"""Regression tests for the session event-loop bootstrap in tests/conftest.py."""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest
from tests.support.repo_paths import REPO_ROOT

_PROBE = textwrap.dedent(
    """
    import asyncio
    import sys

    from tests.support.event_loop import ensure_current_event_loop

    loop = ensure_current_event_loop()
    if sys.version_info >= (3, 12):
        # 3.11's main thread still gets a silent policy loop, so the helper
        # keeps it there; 3.12+ have no current loop to keep.
        assert loop is not None, "a thread with no loop must receive one"
    current = asyncio.get_event_loop()
    assert loop is None or current is loop
    assert not current.is_closed()
    assert ensure_current_event_loop() is None, "an existing loop must be kept"
    assert asyncio.get_event_loop() is current
    current.close()
    asyncio.set_event_loop(None)
    print("ok")
    """
)


@pytest.mark.unit
def test_bootstrap_creates_one_owned_loop_with_warnings_as_errors() -> None:
    """A fresh interpreter has no current loop; -W error mirrors pytest 9.2 configure.

    Python 3.12-3.13 warn and 3.14+ raise from ``asyncio.get_event_loop()``,
    while 3.11 still creates a main-thread loop silently; on each the thread
    must end with exactly one current loop and no leaked warning.
    """
    result = subprocess.run(
        [sys.executable, "-W", "error", "-c", _PROBE],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        stdin=subprocess.DEVNULL,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
    assert "DeprecationWarning" not in result.stderr
