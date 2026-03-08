"""
C++ Language Manager.
"""

import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager


class CppManager(BaseLanguageManager):
    """Manager for the C++ language toolchain."""

    def is_installed(self) -> bool:
        """Check if g++ or clang++ is installed."""
        for cmd in ["g++", "clang++"]:
            try:
                subprocess.run(
                    [cmd, "--version"],
                    check=True,
                    capture_output=True,
                )
                return True
            except FileNotFoundError:
                continue
        return False

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
        except Exception as e:
            print(f"Failed to setup C++ project: {e}")
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write, compile and execute a C++ file."""
        cmd = "g++"
        try:
            subprocess.run(["g++", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            try:
                subprocess.run(["clang++", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                cmd = "clang++"
            except FileNotFoundError:
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
                text=True
            )

            if compile_result.returncode != 0:
                self._cleanup([script_path])
                return "Compilation Failed:\n" + compile_result.stderr

            # Run
            run_result = subprocess.run(
                ["./main_bin"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )

            self._cleanup([script_path, bin_path])
            return run_result.stdout + run_result.stderr

        with tempfile.TemporaryDirectory() as temp_dir:
            return self.use_script(script_content, temp_dir)

    def _cleanup(self, files: list[str]) -> None:
        for file in files:
            try:
                os.remove(file)
            except Exception as _exc:
                pass
