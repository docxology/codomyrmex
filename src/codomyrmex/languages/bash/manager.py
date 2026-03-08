"""
Bash Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)


class BashManager(BaseLanguageManager):
    """Manager for the Bash language shell."""

    _check_commands = [["bash", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Bash. Usually pre-installed."""
        return (
            "### Installing Bash\n\n"
            "Bash is typically pre-installed on macOS and most Linux distributions.\n\n"
            "**macOS (Update via Homebrew):**\n"
            "```bash\n"
            "brew install bash\n"
            "```\n\n"
            "**Alpine Linux (if using containers):**\n"
            "```bash\n"
            "apk add --no-cache bash\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Bash project directory."""
        return self._setup_command(path, lang_name="Bash")

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a Bash script."""
        # Ensure it has a shebang if missing
        if not script_content.startswith("#!"):
            script_content = "#!/usr/bin/env bash\n" + script_content

        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.sh")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            os.chmod(script_path, 0o755)

            result = subprocess.run(
                ["bash", "script.sh"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )
            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".sh", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        os.chmod(temp_path, 0o755)

        try:
            result = subprocess.run(
                ["bash", temp_path],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
