"""
Go Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)


class GoManager(BaseLanguageManager):
    """Manager for the Go language toolchain."""

    _check_commands = [["go", "version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Go."""
        return (
            "### Installing Go\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install go\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y golang-go\n"
            "```\n"
            "**Download:** https://go.dev/doc/install\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Go module."""
        try:
            os.makedirs(path, exist_ok=True)
            mod_name = os.path.basename(os.path.abspath(path))
            if not mod_name:
                mod_name = "example.com/mymodule"

            subprocess.run(
                ["go", "mod", "init", mod_name],
                cwd=path,
                check=True,
                capture_output=True,
            )
            return True
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning("Failed to setup Go project: %s", e)
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a Go script (go run)."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "main.go")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["go", "run", "main.go"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )

            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.TemporaryDirectory() as temp_dir:
            return self.use_script(script_content, temp_dir)
