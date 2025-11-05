#!/usr/bin/env python3
"""
Terminal Utilities for Codomyrmex

Provides utilities for creating engaging terminal interfaces, formatting
output, and running commands with beautiful presentation.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)



class TerminalFormatter:
    """
    Utility class for formatting terminal output with colors and styles.
    """

    # Color codes
    COLORS = {
        "BLACK": "\033[30m",
        "RED": "\033[31m",
        "GREEN": "\033[32m",
        "YELLOW": "\033[33m",
        "BLUE": "\033[34m",
        "MAGENTA": "\033[35m",
        "CYAN": "\033[36m",
        "WHITE": "\033[37m",
        "BRIGHT_BLACK": "\033[90m",
        "BRIGHT_RED": "\033[91m",
        "BRIGHT_GREEN": "\033[92m",
        "BRIGHT_YELLOW": "\033[93m",
        "BRIGHT_BLUE": "\033[94m",
        "BRIGHT_MAGENTA": "\033[95m",
        "BRIGHT_CYAN": "\033[96m",
        "BRIGHT_WHITE": "\033[97m",
    }

    # Style codes
    STYLES = {
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
        "DIM": "\033[2m",
        "ITALIC": "\033[3m",
        "UNDERLINE": "\033[4m",
        "BLINK": "\033[5m",
        "REVERSE": "\033[7m",
        "STRIKETHROUGH": "\033[9m",
    }

    def __init__(self, use_colors: bool = None):
        """Initialize formatter with color support detection."""
        if use_colors is None:
            # Auto-detect color support
            self.use_colors = self._supports_color()
        else:
            self.use_colors = use_colors

    def _supports_color(self) -> bool:
        """Check if terminal supports color output."""
        # Check if we're in a TTY
        if not sys.stdout.isatty():
            return False

        # Check TERM environment variable
        term = os.environ.get("TERM", "").lower()
        if "color" in term or term in ["xterm", "xterm-256color", "screen", "tmux"]:
            return True

        # Check for Windows Terminal or other modern terminals
        if os.environ.get("WT_SESSION") or os.environ.get("COLORTERM"):
            return True

        return False

    def color(self, text: str, color: str, style: Optional[str] = None) -> str:
        """Apply color and style to text."""
        if not self.use_colors:
            return text

        result = ""

        # Add style if specified
        if style and style.upper() in self.STYLES:
            result += self.STYLES[style.upper()]

        # Add color
        if color.upper() in self.COLORS:
            result += self.COLORS[color.upper()]

        # Add text and reset
        result += text + self.STYLES["RESET"]

        return result

    def success(self, text: str) -> str:
        """Format success message."""
        return self.color(f"✅ {text}", "BRIGHT_GREEN")

    def error(self, text: str) -> str:
        """Format error message."""
        return self.color(f"❌ {text}", "BRIGHT_RED")

    def warning(self, text: str) -> str:
        """Format warning message."""
        return self.color(f"⚠️  {text}", "BRIGHT_YELLOW")

    def info(self, text: str) -> str:
        """Format info message."""
        return self.color(f"ℹ️  {text}", "BRIGHT_BLUE")

    def header(self, text: str, char: str = "=", width: int = 60) -> str:
        """Create a formatted header."""
        header_line = char * width
        centered_text = text.center(width)

        result = self.color(header_line, "CYAN") + "\n"
        result += self.color(centered_text, "WHITE", "BOLD") + "\n"
        result += self.color(header_line, "CYAN")

        return result

    def progress_bar(
        self,
        current: int,
        total: int,
        width: int = 40,
        prefix: str = "",
        suffix: str = "",
    ) -> str:
        """Create a progress bar."""
        if total == 0:
            percent = 100
        else:
            percent = min(100, (current / total) * 100)

        filled = int(width * current // total) if total > 0 else width
        bar = "█" * filled + "░" * (width - filled)

        result = f"{prefix} |{bar}| {percent:5.1f}% {suffix}"

        return self.color(result, "BRIGHT_CYAN")

    def table(
        self, headers: list[str], rows: list[list[str]], max_width: int = 80
    ) -> str:
        """Create a formatted table."""
        if not headers or not rows:
            return ""

        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            max_width_col = len(header)
            for row in rows:
                if i < len(row):
                    max_width_col = max(max_width_col, len(str(row[i])))
            col_widths.append(min(max_width_col, max_width // len(headers)))

        # Create table
        result = []

        # Header
        header_row = "│ "
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            header_row += self.color(header[:width].ljust(width), "WHITE", "BOLD")
            if i < len(headers) - 1:
                header_row += " │ "
        header_row += " │"

        # Top border
        top_border = "┌─" + "─┬─".join("─" * width for width in col_widths) + "─┐"
        middle_border = "├─" + "─┼─".join("─" * width for width in col_widths) + "─┤"
        bottom_border = "└─" + "─┴─".join("─" * width for width in col_widths) + "─┘"

        result.append(self.color(top_border, "CYAN"))
        result.append(header_row)
        result.append(self.color(middle_border, "CYAN"))

        # Data rows
        for row in rows:
            data_row = "│ "
            for i, width in enumerate(col_widths):
                value = str(row[i]) if i < len(row) else ""
                data_row += value[:width].ljust(width)
                if i < len(col_widths) - 1:
                    data_row += " │ "
            data_row += " │"
            result.append(data_row)

        result.append(self.color(bottom_border, "CYAN"))

        return "\n".join(result)

    def box(
        self, content: str, title: Optional[str] = None, width: Optional[int] = None
    ) -> str:
        """Create a box around content."""
        lines = content.split("\n")

        if width is None:
            width = max(len(line) for line in lines) + 4
            if title:
                width = max(width, len(title) + 4)

        result = []

        # Top border
        if title:
            title_part = f"┤ {title} ├"
            padding = (width - len(title_part)) // 2
            top_line = (
                "─" * padding + title_part + "─" * (width - len(title_part) - padding)
            )
            result.append(self.color(f"┌{top_line}┐", "CYAN"))
        else:
            result.append(self.color(f"┌{'─' * width}┐", "CYAN"))

        # Content lines
        for line in lines:
            padded_line = line.ljust(width)
            result.append(f"│ {padded_line} │")

        # Bottom border
        result.append(self.color(f"└{'─' * width}┘", "CYAN"))

        return "\n".join(result)


class CommandRunner:
    """
    Utility class for running commands with beautiful output formatting.
    """

    def __init__(self, formatter: Optional[TerminalFormatter] = None):
        """Initialize command runner."""
        self.formatter = formatter or TerminalFormatter()

    def run_command(
        self,
        command: list[str],
        cwd: Optional[Path] = None,
        show_output: bool = True,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Run a command and return formatted results.

        Args:
            command: Command and arguments as list
            cwd: Working directory for command
            show_output: Whether to display output in real-time
            timeout: Timeout in seconds

        Returns:
            Dict with 'returncode', 'stdout', 'stderr', 'success'
        """
        if show_output:
            print(self.formatter.info(f"Running: {' '.join(command)}"))

        try:
            if show_output:
                # Run with real-time output
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                )

                stdout_lines = []
                stderr_lines = []

                # Read output in real-time
                while True:
                    stdout_line = process.stdout.readline()
                    if stdout_line:
                        stdout_lines.append(stdout_line.rstrip())
                        print(f"  {stdout_line.rstrip()}")

                    stderr_line = process.stderr.readline()
                    if stderr_line:
                        stderr_lines.append(stderr_line.rstrip())
                        print(self.formatter.warning(f"  {stderr_line.rstrip()}"))

                    if (
                        stdout_line == ""
                        and stderr_line == ""
                        and process.poll() is not None
                    ):
                        break

                stdout = "\n".join(stdout_lines)
                stderr = "\n".join(stderr_lines)
                returncode = process.returncode

            else:
                # Run without real-time output
                result = subprocess.run(
                    command, cwd=cwd, capture_output=True, text=True, timeout=timeout
                )

                stdout = result.stdout
                stderr = result.stderr
                returncode = result.returncode

            success = returncode == 0

            if show_output:
                if success:
                    print(self.formatter.success("Command completed successfully"))
                else:
                    print(
                        self.formatter.error(
                            f"Command failed with exit code {returncode}"
                        )
                    )

            return {
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr,
                "success": success,
                "command": " ".join(command),
            }

        except subprocess.TimeoutExpired:
            if show_output:
                print(self.formatter.error(f"Command timed out after {timeout}s"))
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "success": False,
                "command": " ".join(command),
            }

        except Exception as e:
            if show_output:
                print(self.formatter.error(f"Command failed: {e}"))
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "command": " ".join(command),
            }

    def run_python_module(
        self,
        module: str,
        args: list[str] = None,
        cwd: Optional[Path] = None,
        show_output: bool = True,
    ) -> dict[str, Any]:
        """Run a Python module with formatting."""
        command = [sys.executable, "-m", module]
        if args:
            command.extend(args)

        return self.run_command(command, cwd, show_output)

    def check_tool_available(self, tool: str) -> bool:
        """Check if a command-line tool is available."""
        return shutil.which(tool) is not None

    def get_system_info(self) -> dict[str, str]:
        """Get system information for diagnostics."""
        info = {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "platform": sys.platform,
            "cwd": str(Path.cwd()),
        }

        # Check for common tools
        tools = ["git", "npm", "node", "docker", "pip", "uv"]
        for tool in tools:
            info[f"{tool}_available"] = str(self.check_tool_available(tool))

        return info

    def run_diagnostic(self) -> None:
        """Run system diagnostic and display results."""
        print(self.formatter.header("SYSTEM DIAGNOSTIC"))

        info = self.get_system_info()

        # Format as table
        headers = ["Component", "Status/Value"]
        rows = []

        for key, value in info.items():
            # Format key nicely
            nice_key = key.replace("_", " ").title()

            # Determine status formatting
            if key.endswith("_available"):
                if value == "True":
                    formatted_value = self.formatter.success("Available")
                else:
                    formatted_value = self.formatter.error("Not Found")
            else:
                formatted_value = value[:50] + "..." if len(value) > 50 else value

            rows.append([nice_key, formatted_value])

        print(self.formatter.table(headers, rows))


def create_ascii_art(text: str, style: str = "simple") -> str:
    """
    Create simple ASCII art for text.

    Args:
        text: Text to convert
        style: Art style ('simple', 'block', etc.)

    Returns:
        ASCII art string
    """
    if style == "simple":
        return text
    elif style == "block":
        # Simple block letters (limited character set)
        block_chars = {
            "A": ["  █  ", " █ █ ", "█████", "█   █", "█   █"],
            "B": ["████ ", "█   █", "████ ", "█   █", "████ "],
            "C": [" ████", "█    ", "█    ", "█    ", " ████"],
            # Add more as needed...
        }

        result = []
        for i in range(5):  # 5 rows for block letters
            row = ""
            for char in text.upper():
                if char in block_chars:
                    row += block_chars[char][i] + " "
                elif char == " ":
                    row += "      "
                else:
                    row += "█████ "
            result.append(row.rstrip())

        return "\n".join(result)

    return text


if __name__ == "__main__":
    # Demo the terminal utilities
    formatter = TerminalFormatter()

    print(formatter.header("TERMINAL UTILITIES DEMO"))

    print(formatter.success("This is a success message"))
    print(formatter.error("This is an error message"))
    print(formatter.warning("This is a warning message"))
    print(formatter.info("This is an info message"))

    print("\n" + formatter.progress_bar(3, 5, prefix="Progress"))

    headers = ["Module", "Status", "Capabilities"]
    rows = [
        ["data_visualization", "Working", "12"],
        ["logging_monitoring", "Working", "8"],
        ["ai_code_editing", "Issues", "15"],
    ]
    print("\n" + formatter.table(headers, rows))

    runner = CommandRunner(formatter)
    runner.run_diagnostic()
