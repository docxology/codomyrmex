"""Tools management mixin for Antigravity IDE client.

Extracted from client.py.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from codomyrmex.ide import IDECommandResult
from codomyrmex.logging_monitoring import get_logger

from .models import CommandExecutionError

logger = get_logger(__name__)


class AntigravityToolsMixin:
    """Mixin for handling Antigravity tools and commands."""

    # Note: Requires self._connected, self.TOOLS, and self.execute_command_safe

    def execute_command(self, command: str, args: dict | None = None) -> Any:
        """Execute an Antigravity command.

        Note: This method simulates command execution. In a real integration,
        this would interface with the actual Antigravity API.

        Args:
            command: Command name to execute.
            args: Optional command arguments.

        Returns:
            Command result.

        Raises:
            CommandExecutionError: If command execution fails.
        """
        if not self._connected:
            raise CommandExecutionError("Not connected to Antigravity session")

        if command not in getattr(self, "TOOLS", []):
            raise CommandExecutionError(f"Unknown command: {command}")

        return {
            "status": "success",
            "command": command,
            "args": args or {},
            "message": f"Command '{command}' executed successfully",
            "timestamp": datetime.now().isoformat(),
        }

    def get_tool_info(self, tool_name: str) -> dict[str, Any] | None:
        """Get information about a specific tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Dict with tool information or None if not found.
        """
        tool_info = {
            "task_boundary": {
                "name": "task_boundary",
                "description": "Manage task state and boundaries",
                "parameters": ["TaskName", "Mode", "TaskStatus", "TaskSummary"],
            },
            "notify_user": {
                "name": "notify_user",
                "description": "Send notification to user",
                "parameters": ["Message", "PathsToReview", "BlockedOnUser"],
            },
            "write_to_file": {
                "name": "write_to_file",
                "description": "Create or overwrite a file",
                "parameters": ["TargetFile", "CodeContent", "IsArtifact"],
            },
            "view_file": {
                "name": "view_file",
                "description": "View file contents",
                "parameters": ["AbsolutePath", "StartLine", "EndLine"],
            },
            "view_file_outline": {
                "name": "view_file_outline",
                "description": "View the outline of a file",
                "parameters": ["AbsolutePath", "ItemOffset"],
            },
            "view_code_item": {
                "name": "view_code_item",
                "description": "View specific code items",
                "parameters": ["File", "NodePaths"],
            },
            "run_command": {
                "name": "run_command",
                "description": "Execute a terminal command",
                "parameters": ["CommandLine", "Cwd", "SafeToAutoRun"],
            },
            "grep_search": {
                "name": "grep_search",
                "description": "Search file contents with ripgrep",
                "parameters": ["SearchPath", "Query", "MatchPerLine"],
            },
            "find_by_name": {
                "name": "find_by_name",
                "description": "Find files by name pattern",
                "parameters": ["SearchDirectory", "Pattern", "Extensions"],
            },
            "list_dir": {
                "name": "list_dir",
                "description": "List directory contents",
                "parameters": ["DirectoryPath"],
            },
            "replace_file_content": {
                "name": "replace_file_content",
                "description": "Replace content in a file",
                "parameters": [
                    "TargetFile",
                    "StartLine",
                    "EndLine",
                    "TargetContent",
                    "ReplacementContent",
                ],
            },
            "multi_replace_file_content": {
                "name": "multi_replace_file_content",
                "description": "Make multiple replacements in a file",
                "parameters": ["TargetFile", "ReplacementChunks"],
            },
        }

        return tool_info.get(tool_name)

    def send_chat_gui(
        self, message: str, app_name: str = "Antigravity"
    ) -> IDECommandResult:
        """Send a message using GUI automation (AppleScript).

        This method bypasses the CLI and sends keystrokes directly to the
        active window of the specified application. Useful for targeting
        specific UI panes that the CLI cannot reach.

        Args:
            message: The message to type.
            app_name: The application name to target (default: "Antigravity").

        Returns:
            IDECommandResult indicating success/failure of the AppleScript execution.
        """
        # Escape double quotes for AppleScript
        safe_message = message.replace('"', '\\"')

        apple_script = f"""
        tell application "{app_name}"
            activate
        end tell

        delay 0.5

        tell application "System Events"
            tell process "{app_name}"
                keystroke "{safe_message}"
                delay 0.1
                key code 36
            end tell
        end tell
        """

        try:
            subprocess.run(
                ["osascript", "-e", apple_script],
                check=True,
                capture_output=True,
                timeout=10,
            )
            return IDECommandResult(
                success=True,
                command="osascript",
                output={"message": message, "method": "gui", "app": app_name},
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            return IDECommandResult(
                success=False,
                command="osascript",
                error=f"GUI automation failed: {error_msg}",
            )
        except Exception as e:
            return IDECommandResult(success=False, command="osascript", error=str(e))

    def invoke_tool(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> IDECommandResult:
        """Invoke an Antigravity tool.

        This is a higher-level method that uses execute_command_safe.

        Args:
            tool_name: Name of the tool to invoke.
            parameters: Tool parameters.

        Returns:
            IDECommandResult with execution details.
        """
        if tool_name not in getattr(self, "TOOLS", []):
            return IDECommandResult(
                success=False,
                command=tool_name,
                error=f"Unknown tool: {tool_name}",
            )

        return self.execute_command_safe(tool_name, parameters)

    def send_chat_message(self, message: str, **kwargs) -> IDECommandResult:
        """Send a message to the Antigravity chat.

        Uses the 'antigravity' or 'agy' CLI if available to send a real message
        to the IDE chat interface. Falls back to simulated tool invocation.

        Args:
            message: The message content to send.
            **kwargs: Additional arguments for notify_user.

        Returns:
            IDECommandResult with the execution result.
        """
        # Try real CLI first
        cli = shutil.which("antigravity") or shutil.which("agy")

        if cli:
            try:
                cmd = [cli, "chat", "--reuse-window"]

                mode = kwargs.get("mode")
                if mode:
                    cmd.extend(["--mode", mode])

                cmd.append(message)

                subprocess.run(cmd, check=True, capture_output=True, timeout=30)

                return IDECommandResult(
                    success=True,
                    command=f"{Path(cli).name} chat",
                    output={
                        "message": message,
                        "method": "cli",
                        "cli_path": cli,
                        "mode": mode or "default",
                    },
                )
            except subprocess.CalledProcessError as e:
                logger.warning("Antigravity CLI notification failed: %s", str(e))
            except Exception as e:
                logger.warning("Antigravity notify_user unexpected error: %s", str(e))

        # Fallback implementation
        if not self._connected:
            return IDECommandResult(
                success=False,
                command="notify_user",
                error="Not connected to Antigravity session",
            )

        params = {
            "Message": message,
            "BlockedOnUser": kwargs.get("BlockedOnUser", False),
            "PathsToReview": kwargs.get("PathsToReview", []),
            "ShouldAutoProceed": kwargs.get("ShouldAutoProceed", False),
        }

        return self.invoke_tool("notify_user", params)
