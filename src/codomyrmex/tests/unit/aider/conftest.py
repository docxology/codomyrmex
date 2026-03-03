"""Shared fixtures and skip guards for aider module tests."""

from __future__ import annotations

import shutil

import pytest

aider_installed = shutil.which("aider") is not None

requires_aider = pytest.mark.skipif(
    not aider_installed, reason="aider not installed: uv tool install aider-chat"
)
