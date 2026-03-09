"""
PHP Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)


class PhpManager(BaseLanguageManager):
    """Manager for the PHP scripting language."""

    _check_commands = [["php", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing PHP."""
        return (
            "### Installing PHP\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install php\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y php\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new PHP project directory."""
        return self._setup_command(path, lang_name="PHP")

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a PHP script."""
        # Ensure it starts with <?php
        if not script_content.strip().startswith("<?php"):
            script_content = "<?php\n" + script_content

        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.php")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["php", "script.php"], cwd=dir_path, capture_output=True, text=True
            )

            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".php", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(["php", temp_path], capture_output=True, text=True)
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
