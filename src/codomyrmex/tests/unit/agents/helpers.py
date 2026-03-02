"""Shared test infrastructure for agent unit tests.

This module provides module-level constants and helper functions used by
agent test files to gate tests on external tool/SDK availability.

**Design rationale — why module-level constants, not pytest fixtures:**

The constants defined here (GEMINI_AVAILABLE, JULES_AVAILABLE, etc.) are
intentionally evaluated at *module import time* (i.e., during pytest
collection), not at test invocation time.  This is required because they
are consumed by ``@pytest.mark.skipif(not CONSTANT, ...)`` decorators,
which are processed when Python parses the test module, before any test
function is called or any pytest fixture is instantiated.

Converting these constants to pytest fixtures would break the skip
mechanism: fixtures are injected at test-call time and cannot be referenced
in decorator arguments that must evaluate to a literal bool at definition
time.

**Usage pattern in test files:**

    from codomyrmex.tests.unit.agents.helpers import GEMINI_AVAILABLE

    class TestGeminiIntegration:
        @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI or SDK not installed")
        def test_something(self):
            ...

**Adding new tools:**  Add a new ``TOOL_AVAILABLE`` constant below following
the existing ``check_tool_available("tool-name")`` pattern.  Do NOT import
this file from production code — it is test infrastructure only.
"""

import os
import subprocess


def check_tool_available(command: str, help_flag: str = "--help") -> bool:
    """
    Check if CLI tool is available.

    Args:
        command: Command name to check
        help_flag: Flag to use for checking (default: "--help")

    Returns:
        True if tool is available, False otherwise
    """
    try:
        result = subprocess.run(
            [command, help_flag],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Tool is available if:
        # 1. Exit code is 0, OR
        # 2. Help text appears in stdout or stderr
        return (
            result.returncode == 0
            or help_flag in (result.stdout or "")
            or help_flag in (result.stderr or "")
            or "--help" in (result.stdout or "")
            or "--help" in (result.stderr or "")
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    except Exception:
        return False


# Check availability of CLI tools and SDKs at module level
try:
    import google.genai as genai  # noqa: F401
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = (SDK_AVAILABLE and GEMINI_API_KEY is not None) or check_tool_available("gemini")
JULES_AVAILABLE = check_tool_available("jules")
OPENCLAW_AVAILABLE = check_tool_available("openclaw")
OPENCODE_AVAILABLE = check_tool_available("opencode")
VIBE_AVAILABLE = check_tool_available("vibe")
EVERY_CODE_AVAILABLE = check_tool_available("code") or check_tool_available("coder")


def get_tool_version(command: str) -> str | None:
    """
    Get version of CLI tool if available.

    Args:
        command: Command name

    Returns:
        Version string if available, None otherwise
    """
    if not check_tool_available(command):
        return None

    try:
        # Try common version flags
        for flag in ["--version", "-v", "-V", "version"]:
            result = subprocess.run(
                [command, flag],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
    except Exception:
        pass

    return None

