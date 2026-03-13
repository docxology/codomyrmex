"""
R Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)
_TIMEOUT_FAST = 10  # seconds for version checks
_TIMEOUT_SLOW = 300  # seconds for script/build execution


class RManager(BaseLanguageManager):
    """Manager for the R programming language toolchain."""

    _check_commands = [["Rscript", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing R."""
        return (
            "### Installing R\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install r\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y r-base\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new R project directory."""
        return self._setup_command(path, lang_name="R")

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute an R script using Rscript."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.R")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["Rscript", "script.R"],
                cwd=dir_path,
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_SLOW,
            )

            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".R", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                ["Rscript", temp_path],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_SLOW,
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
