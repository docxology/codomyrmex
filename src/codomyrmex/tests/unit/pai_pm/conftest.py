"""Shared fixtures and marks for pai_pm tests."""

from __future__ import annotations

import shutil

import pytest

bun_installed: bool = shutil.which("bun") is not None

requires_bun = pytest.mark.skipif(
    not bun_installed,
    reason="bun runtime not installed",
)

# Server tests are always skipped in unit suite — server startup is a side effect
requires_running_server = pytest.mark.skipif(
    True,
    reason="requires running PAI PM server (integration test only)",
)
