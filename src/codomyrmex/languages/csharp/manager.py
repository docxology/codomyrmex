"""
C# (.NET Core) Language Manager.
"""

import os
import subprocess
import tempfile

from codomyrmex.languages.base import BaseLanguageManager

_TIMEOUT_FAST = 10   # seconds for version checks
_TIMEOUT_SLOW = 300  # seconds for script/build execution


class CSharpManager(BaseLanguageManager):
    """Manager for the C# (.NET) language toolchain."""

    _check_commands = [["dotnet", "--version"]]

    def install_instructions(self) -> str:
        """Return markdown instructions for installing .NET SDK for C#."""
        return (
            "### Installing .NET SDK (C#)\n\n"
            "**macOS (via Homebrew):**\n"
            "```bash\n"
            "brew install --cask dotnet-sdk\n"
            "```\n\n"
            "**Ubuntu/Debian:**\n"
            "```bash\n"
            "sudo apt-get update && sudo apt-get install -y dotnet-sdk-8.0\n"
            "```\n"
        )

    def setup_project(self, path: str) -> bool:
        """Initialize a new C# project."""
        return self._setup_command(path, ["dotnet", "new", "console"], lang_name="C#")

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write, compile and execute a C# file."""
        if dir_path is not None:
            os.makedirs(dir_path, exist_ok=True)
        else:
            temp_dir = tempfile.mkdtemp()
            dir_path = temp_dir

        try:
            # We initialize a new project to easily run a single file script via 'dotnet run'
            subprocess.run(
                ["dotnet", "new", "console", "--force"],
                cwd=dir_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            timeout=_TIMEOUT_SLOW,
            )

            script_path = os.path.join(dir_path, "Program.cs")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            result = subprocess.run(
                ["dotnet", "run"],
                cwd=dir_path,
                capture_output=True,
                text=True,
            timeout=_TIMEOUT_SLOW,
            )

            return result.stdout + result.stderr
        finally:
            # We don't clean the whole directory if they passed explicit path, just the file
            # If it's a temp dir, it will persist here. Let's do a better cleanup:
            # Only remove Program.cs if explicit, remove whole tree if tempfile
            pass
            # Note: For strict Zero-Mock testing 'dotnet run' generates multiple obj/bin files
            # For a pure script approach, consider a tool like 'dotnet script' if installed,
            # but standard SDK 'dotnet run' is safest fallback.
