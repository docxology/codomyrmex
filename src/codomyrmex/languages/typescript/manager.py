"""
TypeScript Language Manager.
"""

import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager
from codomyrmex.languages.javascript.manager import JavaScriptManager


class TypeScriptManager(BaseLanguageManager):
    """Manager for the TypeScript language toolchain."""

    def is_installed(self) -> bool:
        """Check if ts-node or bun or tsc is installed. We prefer bun if available, else require ts-node."""
        if self._has_cmd("bun"):
            return True

        # If no bun, we check node and ts-node or npx
        # Instead of strict global install check, if node is installed, npx tsx/ts-node usually works
        return JavaScriptManager().is_installed()

    def install_instructions(self) -> str:
        """Return markdown instructions for installing TypeScript execution tools."""
        return (
            "### Installing TypeScript Runtime\n\n"
            "TypeScript needs a compiler or runtime. Codomyrmex recommends `bun` or `tsx`.\n\n"
            "**Installing Bun (Recommended):**\n"
            "```bash\n"
            "curl -fsSL https://bun.sh/install | bash\n"
            "```\n\n"
            "**Installing tsx (via npm):**\n"
            "Requires Node.js installed.\n"
            "```bash\n"
            "npm install -g tsx typescript\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new TypeScript project."""
        try:
            os.makedirs(path, exist_ok=True)

            if self._has_cmd("bun"):
                subprocess.run(["bun", "init", "-y"], cwd=path, check=True, capture_output=True)
                return True

            # Fallback npm and tsc
            subprocess.run(["npm", "init", "-y"], cwd=path, check=True, capture_output=True)
            subprocess.run(["npx", "tsc", "--init"], cwd=path, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Failed to setup TS project: {e}")
            return False

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write and execute a TypeScript script."""

        cmd = []
        if self._has_cmd("bun"):
            cmd = ["bun", "run"]
        elif self._has_cmd("tsx"):
            cmd = ["tsx"]
        else:
            # Fallback to npx tsx
            cmd = ["npx", "tsx"]

        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
            script_path = os.path.join(dir_path, "script.ts")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                [*cmd, "script.ts"],
                cwd=dir_path,
                capture_output=True,
                text=True
            )
            self._cleanup([script_path])
            return result.stdout + result.stderr

        with tempfile.NamedTemporaryFile(suffix=".ts", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                [*cmd, temp_path],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        finally:
            os.remove(temp_path)

    def _has_cmd(self, cmd: str) -> bool:
        try:
            subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False
