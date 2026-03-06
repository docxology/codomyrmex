"""
Swift Language Manager.
"""

import os
import subprocess
import tempfile


class SwiftManager:
    """Manager for the Swift language toolchain."""

    def is_installed(self) -> bool:
        """Check if swift is installed."""
        try:
            subprocess.run(
                ["swift", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Swift."""
        return (
            "### Installing Swift\n\n"
            "**macOS:**\n"
            "Swift is included with Xcode. Install Xcode via the Mac App Store, or the command line tools:\n"
            "```bash\n"
            "xcode-select --install\n"
            "```\n\n"
            "**Linux/Ubuntu:**\n"
            "See exact instructions at https://swift.org/download/\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Swift project."""
        try:
            os.makedirs(path, exist_ok=True)
            subprocess.run(
                ["swift", "package", "init", "--type", "executable"],
                cwd=path,
                check=True,
                capture_output=True,
            )
            return True
        except Exception as e:
            print(f"Failed to setup Swift project: {e}")
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a Swift script."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.swift")

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["swift", "script.swift"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )

            try:
                os.remove(script_path)
            except Exception:
                pass
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".swift", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                ["swift", temp_path],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
