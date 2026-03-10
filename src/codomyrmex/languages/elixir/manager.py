"""
Elixir Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)
_TIMEOUT_FAST = 10   # seconds for version checks
_TIMEOUT_SLOW = 300  # seconds for script/build execution


class ElixirManager(BaseLanguageManager):
    """Manager for the Elixir programming language toolchain."""

    _check_commands = [["elixir", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Elixir."""
        return (
            "### Installing Elixir\n\n"
            "Requires Erlang first. Elixir installers usually handle this.\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install elixir\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y elixir\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Elixir project using mix."""
        try:
            app_name = os.path.basename(os.path.abspath(path))
            # Mix creates the directory if it doesn't exist, but requires non-empty name
            if not app_name:
                app_name = "example_app"

            # Run mix new outside the path if we want the path to be the container
            parent_dir = os.path.dirname(os.path.abspath(path))

            subprocess.run(
                ["mix", "new", app_name],
                cwd=parent_dir,
                check=True,
                capture_output=True,
            timeout=_TIMEOUT_SLOW,
            )
            return True
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning("Failed to setup Elixir project: %s", e)
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute an Elixir script using the `elixir` command."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.exs")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["elixir", "script.exs"],
                cwd=dir_path,
                capture_output=True,
                text=True,
            timeout=_TIMEOUT_SLOW,
            )

            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".exs", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                ["elixir", temp_path],
                capture_output=True,
                text=True,
            timeout=_TIMEOUT_SLOW,
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
