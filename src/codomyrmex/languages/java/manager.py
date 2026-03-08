"""
Java Language Manager.
"""

import os
import re
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager


class JavaManager(BaseLanguageManager):
    """Manager for the Java language toolchain."""

    _check_commands = [["javac", "--version"], ["java", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Java."""
        return (
            "### Installing Java (JDK)\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install openjdk\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y default-jdk\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new basic Java directory layout."""
        try:
            os.makedirs(os.path.join(path, "src", "main", "java"), exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to setup Java project: {e}")
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write, compile and execute a Java class."""

        # Try to find class name to name the file correctly
        class_match = re.search(r"class\s+([A-Za-z0-9_]+)", script_content)
        class_name = class_match.group(1) if class_match else "Main"
        file_name = f"{class_name}.java"

        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, file_name)

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            # Compile
            compile_result = subprocess.run(
                ["javac", file_name],
                cwd=dir_path,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                self._cleanup([script_path])
                return "Compilation Failed:\n" + compile_result.stderr

            # Run
            run_result = subprocess.run(
                ["java", class_name],
                cwd=dir_path,
                capture_output=True,
                text=True
            )

            self._cleanup([script_path, os.path.join(dir_path, f"{class_name}.class")])
            return run_result.stdout + run_result.stderr

        with tempfile.TemporaryDirectory() as temp_dir:
            return self.use_script(script_content, temp_dir)

