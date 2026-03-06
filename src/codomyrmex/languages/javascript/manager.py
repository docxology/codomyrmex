"""
JavaScript (Node.js) Language Manager.
"""

import os
import subprocess
import tempfile


class JavaScriptManager:
    """Manager for the JavaScript (Node.js) language toolchain."""

    def is_installed(self) -> bool:
        """Check if Node.js is installed."""
        try:
            subprocess.run(
                ["node", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def install_instructions(self) -> str:
        """Return markdown instructions for installing Node.js."""
        return (
            "### Installing Node.js\n\n"
            "**macOS/Linux (via nvm - Node Version Manager):**\n"
            "```bash\n"
            "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash\n"
            "nvm install 20\n"
            "nvm use 20\n"
            "```\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install node@20\n"
            "```\n\n"
            "**Ubuntu/Debian (via NodeSource):**\n"
            "```bash\n"
            "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -\n"
            "sudo apt-get install -y nodejs\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new Node.js project."""
        try:
            os.makedirs(path, exist_ok=True)
            subprocess.run(
                ["npm", "init", "-y"],
                cwd=path,
                check=True,
                capture_output=True,
            )
            return True
        except Exception as e:
            print(f"Failed to setup JS project: {e}")
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a JavaScript script using node."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.js")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["node", "script.js"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )
            try:
                os.remove(script_path)
            except Exception:
                pass
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                ["node", temp_path],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)
