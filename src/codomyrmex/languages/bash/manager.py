"""
Bash Language Manager.
"""

import os
import subprocess
import tempfile


class BashManager:
    """Manager for the Bash language shell."""

    def is_installed(self) -> bool:
        """Check if bash is installed."""
        try:
            subprocess.run(
                ["bash", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

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
        """Initialize a new directory for Bash scripts."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to setup Bash dir: {e}")
            return False

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
            try:
                os.remove(script_path)
            except Exception:
                pass
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
