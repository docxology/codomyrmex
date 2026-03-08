"""
Ruby Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)


class RubyManager(BaseLanguageManager):
    """Manager for the Ruby language toolchain."""

    _check_commands = [["ruby", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Ruby."""
        return (
            "### Installing Ruby\n\n"
            "**macOS:**\n"
            "```bash\n"
            "brew install ruby\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y ruby-full\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Ruby project."""
        return self._setup_command(path, ["bundle", "init"], lang_name="Ruby")

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a Ruby script."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.rb")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["ruby", "script.rb"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )

            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".rb", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                ["ruby", temp_path],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
