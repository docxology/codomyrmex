"""
MCP Tool definitions for the Languages module.
"""

from typing import Any

# We will lazily import the managers to avoid slow startup or dependency issues
# if a tool is not actually called.


def mcp_check_language_installed(language: str) -> str:
    """Check if a specific programming language is installed on the system.

    Returns a boolean string "True" or "False".
    """
    try:
        if language == "python":
            from .python.manager import PythonManager

            return str(PythonManager().is_installed())
        if language in {"javascript", "node"}:
            from .javascript.manager import JavaScriptManager

            return str(JavaScriptManager().is_installed())
        if language == "typescript":
            from .typescript.manager import TypeScriptManager

            return str(TypeScriptManager().is_installed())
        if language == "bash":
            from .bash.manager import BashManager

            return str(BashManager().is_installed())
        if language == "r":
            from .r.manager import RManager

            return str(RManager().is_installed())
        if language == "elixir":
            from .elixir.manager import ElixirManager

            return str(ElixirManager().is_installed())
        if language == "swift":
            from .swift.manager import SwiftManager

            return str(SwiftManager().is_installed())
        if language == "php":
            from .php.manager import PhpManager

            return str(PhpManager().is_installed())
        if language in {"csharp", "dotnet"}:
            from .csharp.manager import CSharpManager

            return str(CSharpManager().is_installed())
        # Generic fallback check
        import shutil

        if shutil.which(language):
            return "True"
        return f"False (Executable '{language}' not found in PATH)"
    except Exception as e:
        return f"Error checking installation: {e}"


def mcp_get_language_install_instructions(language: str) -> str:
    """Get installation instructions for a specific programming language."""
    try:
        if language == "python":
            from .python.manager import PythonManager

            return PythonManager().install_instructions()
        if language in {"javascript", "node"}:
            from .javascript.manager import JavaScriptManager

            return JavaScriptManager().install_instructions()
        if language == "typescript":
            from .typescript.manager import TypeScriptManager

            return TypeScriptManager().install_instructions()
        if language == "bash":
            from .bash.manager import BashManager

            return BashManager().install_instructions()
        if language == "r":
            from .r.manager import RManager

            return RManager().install_instructions()
        if language == "elixir":
            from .elixir.manager import ElixirManager

            return ElixirManager().install_instructions()
        if language == "swift":
            from .swift.manager import SwiftManager

            return SwiftManager().install_instructions()
        if language == "php":
            from .php.manager import PhpManager

            return PhpManager().install_instructions()
        if language in {"csharp", "dotnet"}:
            from .csharp.manager import CSharpManager

            return CSharpManager().install_instructions()
        return f"Error: Language '{language}' not explicitly supported for install instructions. Use system package manager."
    except Exception as e:
        return f"Error getting instructions: {e}"


def mcp_run_language_script(language: str, script_content: str) -> str:
    """Run a script written in a specific language and return the output.

    Warning: This executes arbitrary code on the host system.
    """
    try:
        if language == "python":
            from .python.manager import PythonManager

            return PythonManager().use_script(script_content)
        if language in {"javascript", "node"}:
            from .javascript.manager import JavaScriptManager

            return JavaScriptManager().use_script(script_content)
        if language == "typescript":
            from .typescript.manager import TypeScriptManager

            return TypeScriptManager().use_script(script_content)
        if language == "bash":
            from .bash.manager import BashManager

            return BashManager().use_script(script_content)
        if language == "r":
            from .r.manager import RManager

            return RManager().use_script(script_content)
        if language == "elixir":
            from .elixir.manager import ElixirManager

            return ElixirManager().use_script(script_content)
        if language == "swift":
            from .swift.manager import SwiftManager

            return SwiftManager().use_script(script_content)
        if language == "php":
            from .php.manager import PhpManager

            return PhpManager().use_script(script_content)
        if language in {"csharp", "dotnet"}:
            from .csharp.manager import CSharpManager

            return CSharpManager().use_script(script_content)
        # Generic fallback run attempt
        import os
        import shutil
        import subprocess
        import tempfile

        if not shutil.which(language):
            return f"Error: Executable '{language}' not found in PATH for generic execution."

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as temp:
            temp.write(script_content)
            temp_path = temp.name

        try:
            result = subprocess.run(
                [language, temp_path], capture_output=True, text=True
            )
            return result.stdout + result.stderr
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass
    except Exception as e:
        return f"Error running script: {e}"


def register_mcp_tools(mcp_server: Any) -> None:
    """Register all MCP tools provided by the languages module."""

    # Note: Using the standard Codomyrmex pattern for FastMCP registration
    @mcp_server.tool()
    def check_language_installed(language: str) -> str:
        """Check if a specific programming language is installed on the system."""
        return mcp_check_language_installed(language)

    @mcp_server.tool()
    def get_language_install_instructions(language: str) -> str:
        """Get installation instructions for a specific programming language."""
        return mcp_get_language_install_instructions(language)

    @mcp_server.tool()
    def run_language_script(language: str, script_content: str) -> str:
        """Run a script written in a specific language and return the output."""
        return mcp_run_language_script(language, script_content)
