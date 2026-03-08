"""
PHP Language Manager.
"""

import os
import subprocess
import tempfile


class PhpManager:
    """Manager for the PHP scripting language."""

    def is_installed(self) -> bool:
        """Check if php is installed."""
        try:
            subprocess.run(
                ["php", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

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
        """Initialize a basic PHP project."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to setup PHP project: {e}")
            return False

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
                ["php", "script.php"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )

            try:
                os.remove(script_path)
            except Exception as _exc:
                pass
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".php", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                ["php", temp_path],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
