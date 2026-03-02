import os
import subprocess

"""Helper functions for agent tests.



Tests use real implementations only. When CLI tools are not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

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

