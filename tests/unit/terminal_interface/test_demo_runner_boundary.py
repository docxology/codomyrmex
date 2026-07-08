"""Tests for injected terminal demo execution."""

import io
import sys

import pytest

from codomyrmex.terminal_interface.shells.interactive_shell import InteractiveShell

pytestmark = pytest.mark.unit


def _make_shell_with_runner(runner):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        shell = InteractiveShell(demo_runner=runner)
    finally:
        sys.stdout = old
    return shell


def _capture(method, arg: str = "") -> str:
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        method(arg)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_specific_demo_uses_injected_runner_without_discovery() -> None:
    calls: list[str] = []

    def runner(module_name: str) -> bool:
        calls.append(module_name)
        return True

    shell = _make_shell_with_runner(runner)
    shell.discovery = None

    _capture(shell._demo_specific_module, "coding")

    assert calls == ["coding"]


def test_missing_runner_reports_no_specific_demo() -> None:
    shell = _make_shell_with_runner(None)
    shell.discovery = None

    output = _capture(shell._demo_code_execution)

    assert "No coding demo runner configured" in output
