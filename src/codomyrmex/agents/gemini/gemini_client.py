"""Gemini CLI client wrapper."""

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Iterator, Optional

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.exceptions import GeminiError
from codomyrmex.agents.generic import BaseAgent
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GeminiClient(BaseAgent):
    """Client for interacting with Gemini CLI tool."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Gemini client.

        Args:
            config: Optional configuration override
        """
        agent_config = get_config()
        super().__init__(
            name="gemini",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            config=config or {},
        )

        self.gemini_command = (
            config.get("gemini_command")
            if config
            else agent_config.gemini_command
        )
        self.timeout = (
            config.get("gemini_timeout")
            if config
            else agent_config.gemini_timeout
        )
        self.working_dir = (
            config.get("gemini_working_dir")
            if config
            else agent_config.gemini_working_dir
        )
        self.api_key = (
            config.get("gemini_api_key")
            if config
            else agent_config.gemini_api_key
        )
        self.auth_method = (
            config.get("gemini_auth_method")
            if config
            else agent_config.gemini_auth_method
        )
        self.settings_path = (
            config.get("gemini_settings_path")
            if config
            else agent_config.gemini_settings_path
        )
        self.enable_shell_commands = config.get(
            "gemini_enable_shell_commands", False
        ) if config else False

        # Verify gemini is available
        if not self._check_gemini_available():
            logger.warning("Gemini command not found, some operations may fail")

    def _check_gemini_available(self) -> bool:
        """
        Check if gemini command is available.

        Returns:
            True if gemini is available
        """
        try:
            result = subprocess.run(
                [self.gemini_command, "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 or "--help" in result.stdout or "--help" in result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Gemini command.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        start_time = time.time()

        try:
            prompt = request.prompt
            context = request.context or {}

            # Build gemini command input
            gemini_input = self._build_gemini_input(prompt, context)

            # Execute gemini command
            result = self._execute_gemini_command(gemini_input)

            execution_time = time.time() - start_time

            output = result.get("output", "")
            exit_code = result.get("exit_code", 0)
            stderr_output = result.get("stderr", "")
            success = result.get("success", exit_code == 0)

            error = None
            if not success and stderr_output:
                error = stderr_output
            elif not success and not output:
                error = f"Gemini command failed with exit code {exit_code}"

            return AgentResponse(
                content=output,
                error=error,
                metadata={
                    "command": self.gemini_command,
                    "exit_code": exit_code,
                    "stdout": result.get("stdout", ""),
                    "stderr": stderr_output,
                    "gemini_success": success,
                    "input": gemini_input[:200] if len(gemini_input) > 200 else gemini_input,
                },
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            error_msg = f"Gemini command timed out after {self.timeout}s"
            return AgentResponse(
                content="",
                error=error_msg,
                metadata={
                    "command": self.gemini_command,
                    "timeout": self.timeout,
                },
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Gemini command failed: {str(e)}"
            logger.error(f"Gemini execution error: {e}", exc_info=True)
            return AgentResponse(
                content="",
                error=error_msg,
                metadata={
                    "command": self.gemini_command,
                    "exception": str(e),
                },
                execution_time=execution_time,
            )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Gemini command output.

        Args:
            request: Agent request

        Yields:
            Chunks of output
        """
        prompt = request.prompt
        context = request.context or {}

        gemini_input = self._build_gemini_input(prompt, context)

        try:
            process = subprocess.Popen(
                [self.gemini_command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.working_dir,
                bufsize=1,  # Line buffered
            )

            # Send input
            if gemini_input:
                process.stdin.write(gemini_input)
                process.stdin.close()

            # Stream stdout line by line
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield line.rstrip()
                else:
                    break

            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read()
                if stderr:
                    yield f"Error: {stderr}"

        except Exception as e:
            logger.error(f"Error streaming Gemini output: {e}", exc_info=True)
            yield f"Error: {str(e)}"

    def _build_gemini_input(self, prompt: str, context: dict[str, Any]) -> str:
        """
        Build gemini command input from prompt and context.

        Args:
            prompt: User prompt
            context: Additional context (may include files, commands, etc.)

        Returns:
            Formatted input string for Gemini CLI
        """
        # Handle different input types
        input_parts = []

        # Handle @ commands (file inclusion)
        if "@" in prompt:
            # Extract @ commands and validate file paths
            parts = prompt.split("@")
            for i, part in enumerate(parts):
                if i == 0:
                    input_parts.append(part)
                else:
                    # Extract file path from @command
                    file_part = part.split()[0] if part.split() else ""
                    if file_part and Path(file_part).exists():
                        input_parts.append(f"@{file_part}")
                        input_parts.append(part[len(file_part):].lstrip())
                    else:
                        input_parts.append(f"@{part}")
        else:
            input_parts.append(prompt)

        # Handle ! commands (shell execution) - only if enabled
        if "!" in prompt and not self.enable_shell_commands:
            logger.warning("Shell commands (!) are disabled. Enable via config to use.")
            # Remove ! commands or replace with comment
            input_parts = [p.replace("!", "# ") if p.strip().startswith("!") else p for p in input_parts]

        # Handle context parameters
        if "files" in context:
            for file_path in context["files"]:
                if Path(file_path).exists():
                    input_parts.insert(0, f"@{file_path}\n")

        if "directories" in context:
            for dir_path in context["directories"]:
                if Path(dir_path).is_dir():
                    input_parts.insert(0, f"@directory {dir_path}\n")

        # Join all parts
        return "\n".join(input_parts)

    def _execute_gemini_command(self, input_text: str) -> dict[str, Any]:
        """
        Execute gemini command and return result.

        Args:
            input_text: Input text to send to Gemini CLI

        Returns:
            Command result dictionary
        """
        try:
            # Set up environment
            env = os.environ.copy()
            if self.api_key and self.auth_method == "api_key":
                env["GEMINI_API_KEY"] = self.api_key

            result = subprocess.run(
                [self.gemini_command],
                input=input_text,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir,
                env=env,
            )

            output = result.stdout.strip()
            stderr_output = result.stderr.strip()

            return {
                "output": output,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0 or (output and not stderr_output),
            }
        except subprocess.TimeoutExpired:
            raise GeminiError(
                "Gemini command timed out",
                command=self.gemini_command,
            )
        except FileNotFoundError:
            raise GeminiError(
                f"Gemini command not found: {self.gemini_command}",
                command=self.gemini_command,
            )

    def execute_gemini_command(
        self, command: str, args: Optional[list[str]] = None, input_text: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Execute a gemini slash command.

        Args:
            command: Gemini command name (e.g., "/model", "/settings")
            args: Optional command arguments
            input_text: Optional input text to send

        Returns:
            Command result dictionary
        """
        # Build command input
        cmd_input = command
        if args:
            cmd_input += " " + " ".join(args)
        if input_text:
            cmd_input += "\n" + input_text

        return self._execute_gemini_command(cmd_input)

    def get_gemini_help(self) -> dict[str, Any]:
        """
        Get gemini help information.

        Returns:
            Help information dictionary
        """
        try:
            result = subprocess.run(
                [self.gemini_command, "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            return {
                "help_text": result.stdout or result.stderr,
                "exit_code": result.returncode,
                "available": result.returncode == 0 or "--help" in (result.stdout or result.stderr),
            }
        except Exception as e:
            return {
                "help_text": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

    def save_chat(self, tag: str, prompt: Optional[str] = None) -> dict[str, Any]:
        """
        Save current chat session.

        Args:
            tag: Tag for identifying the conversation
            prompt: Optional prompt to save

        Returns:
            Save result dictionary
        """
        cmd = f"/chat save {tag}"
        if prompt:
            cmd += f"\n{prompt}"

        return self.execute_gemini_command("/chat", ["save", tag], prompt)

    def resume_chat(self, tag: str) -> dict[str, Any]:
        """
        Resume a saved chat session.

        Args:
            tag: Tag of the conversation to resume

        Returns:
            Resume result dictionary
        """
        return self.execute_gemini_command("/chat", ["resume", tag])

    def list_chats(self) -> dict[str, Any]:
        """
        List available chat sessions.

        Returns:
            List of available chats
        """
        return self.execute_gemini_command("/chat", ["list"])

