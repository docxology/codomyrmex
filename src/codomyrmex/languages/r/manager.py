"""
R Language Manager.
"""

import os
import subprocess
import tempfile


class RManager:
    """Manager for the R programming language toolchain."""

    def is_installed(self) -> bool:
        """Check if Rscript is installed."""
        try:
            subprocess.run(
                ["Rscript", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

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
        """Initialize a basic R project space."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to setup R project: {e}")
            return False

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
                text=True
            )

            try:
                os.remove(script_path)
            except Exception as _exc:
                pass
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".R", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                ["Rscript", temp_path],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
