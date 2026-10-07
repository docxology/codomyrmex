"""
C++ Language Manager.
"""

import logging
import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

logger = logging.getLogger(__name__)
_TIMEOUT_FAST = 10  # seconds for version checks
# The first g++/clang++ call on a fresh macOS runner goes through xcrun and
# can take well over 10 s; a generous ceiling costs nothing when it is fast.
_TIMEOUT_PROBE = 60
_TIMEOUT_SLOW = 300  # seconds for script/build execution


class CppManager(BaseLanguageManager):
    """Manager for the C++ language toolchain."""

    def _compiler(self) -> str | None:
        """Return the first working compiler (``g++`` then ``clang++``).

        A compiler counts only if ``--version`` exits 0 within the probe
        timeout. Missing binaries, non-zero exits (macOS ships ``g++`` shims
        that fail without the Command Line Tools) and timeouts all mean "not
        this one" instead of escaping as exceptions.
        """
        for cmd in ("g++", "clang++"):
            try:
                subprocess.run(
                    [cmd, "--version"],
                    check=True,
                    capture_output=True,
                    timeout=_TIMEOUT_PROBE,
                )
            except (FileNotFoundError, subprocess.SubprocessError):
                continue
            return cmd
        return None

    def is_installed(self) -> bool:
        """Check if g++ or clang++ is installed and runs."""
        return self._compiler() is not None

    def install_instructions(self) -> str:
        """Return markdown instructions for installing C++ compiler."""
        return (
            "### Installing C++ (g++/clang++)\n\n"
            "**macOS:**\n"
            "```bash\n"
            "xcode-select --install\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y build-essential\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new basic C++ directory layout."""
        try:
            os.makedirs(os.path.join(path, "src"), exist_ok=True)
            return True
        except OSError as e:
            logger.warning("Failed to setup C++ project: %s", e)
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write, compile and execute a C++ file."""
        cmd = self._compiler()
        if cmd is None:
            return "Error: Neither g++ nor clang++ found."

        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "main.cpp")
            bin_path = os.path.join(dir_path, "main_bin")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            # Compile
            compile_result = subprocess.run(
                [cmd, "main.cpp", "-o", "main_bin"],
                cwd=dir_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if compile_result.returncode != 0:
                self._cleanup([script_path])
                return "Compilation Failed:\n" + compile_result.stderr

            # Run
            run_result = subprocess.run(
                ["./main_bin"],
                cwd=dir_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self._cleanup([script_path, bin_path])
            return run_result.stdout + run_result.stderr

        with tempfile.TemporaryDirectory() as temp_dir:
            return self.use_script(script_content, temp_dir)
