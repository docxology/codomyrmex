"""
Python Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)
_TIMEOUT_FAST = 10   # seconds for version checks
_TIMEOUT_SLOW = 300  # seconds for script/build execution


class PythonManager(BaseLanguageManager):
    """Manager for the Python language toolchain."""

    def is_installed(self) -> bool:
        """Check if Python 3 is installed. Prefer python3 over python if available."""
        try:
            # We check both python3 and python, prioritizing python3.
            for cmd in ["python3", "python"]:
                try:
                    subprocess.run(
                        [cmd, "--version"],
                        check=True,
                        capture_output=True,
                    timeout=_TIMEOUT_FAST,
                    )
                    return True
                except FileNotFoundError:
                    continue
            return False
        except Exception as _exc:
            return False

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Python."""
        return (
            "### Installing Python 3\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install python3\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt update && sudo apt install -y python3 python3-pip python3-venv\n"
            "```\n\n"
            "**uv (Recommended by Codomyrmex for environment management):**\n"
            "Codomyrmex prefers using `uv` for Python environments.\n"
            "```bash\n"
            "curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Python project using uv."""
        try:
            os.makedirs(path, exist_ok=True)
            # Try uv first
            try:
                subprocess.run(
                    ["uv", "init"],
                    cwd=path,
                    check=True,
                    capture_output=True,
                timeout=_TIMEOUT_SLOW,
                )
                return True
            except FileNotFoundError:
                # Fallback to standard python venv
                cmd = "python3" if self._has_cmd("python3") else "python"
                subprocess.run(
                    [cmd, "-m", "venv", ".venv"],
                    cwd=path,
                    check=True,
                    capture_output=True,
                timeout=_TIMEOUT_SLOW,
                )
                return True
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning("Failed to setup Python project: %s", e)
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a Python script."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            cmd = "python3" if self._has_cmd("python3") else "python"
            result = subprocess.run(
                [cmd, "script.py"],
                cwd=dir_path,
                capture_output=True,
                text=True,
            timeout=_TIMEOUT_SLOW,
            )
            # Clean up immediately after run
            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            cmd = "python3" if self._has_cmd("python3") else "python"
            result = subprocess.run(
                [cmd, temp_path],
                capture_output=True,
                text=True,
            timeout=_TIMEOUT_SLOW,
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)

    def _has_cmd(self, cmd: str) -> bool:
        try:
            subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=_TIMEOUT_FAST)
            return True
        except FileNotFoundError:
            return False
