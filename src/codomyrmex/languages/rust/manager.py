"""
Rust Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)


class RustManager(BaseLanguageManager):
    """Manager for the Rust language toolchain."""

    _check_commands = [["cargo", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Rust."""
        return (
            "### Installing Rust\n\n"
            "**macOS/Linux (via rustup):**\n"
            "```bash\n"
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Rust project using cargo."""
        try:
            subprocess.run(
                ["cargo", "new", path],
                check=True,
                capture_output=True,
            )
            return True
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning("Failed to setup Rust project: %s", e)
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a Rust script. Uses rustc to compile and then runs it."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.rs")
            bin_path = os.path.join(dir_path, "script_bin")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            # Compile
            compile_result = subprocess.run(
                ["rustc", "script.rs", "-o", "script_bin"],
                cwd=dir_path,
                capture_output=True,
                text=True,
            )

            if compile_result.returncode != 0:
                self._cleanup([script_path])
                return "Compilation Failed:\n" + compile_result.stderr

            # Run
            run_result = subprocess.run(
                ["./script_bin"], cwd=dir_path, capture_output=True, text=True
            )

            self._cleanup([script_path, bin_path])
            return run_result.stdout + run_result.stderr

        with tempfile.TemporaryDirectory() as temp_dir:
            return self.use_script(script_content, temp_dir)
