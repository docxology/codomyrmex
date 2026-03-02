import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

logger = get_logger(__name__)

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import (
    AgentError,
    AgentTimeoutError,
    EveryCodeError,
)
from codomyrmex.agents.generic import CLIAgentBase
from codomyrmex.logging_monitoring.core.logger_config import get_logger


class EveryCodeClient(CLIAgentBase):
    """Client for interacting with Every Code CLI tool."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Every Code client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="every_code",
            command="code",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            config=config or {},
            timeout=120,
            working_dir=None,
            env_vars={},
        )

        code_command = self.get_config_value("every_code_command", config=config)
        alt_command = self.get_config_value("every_code_alt_command", config=config)
        timeout = self.get_config_value("every_code_timeout", config=config)
        working_dir_str = self.get_config_value("every_code_working_dir", config=config)
        working_dir = Path(working_dir_str) if working_dir_str else None

        available_command = self._find_available_command(code_command, alt_command)

        api_key = self.get_config_value("every_code_api_key", config=config)
        config_path = self.get_config_value("every_code_config_path", config=config)
        if api_key:
            self.env_vars["OPENAI_API_KEY"] = api_key
        if config_path:
            self.env_vars["CODE_HOME"] = config_path

        self.command = available_command
        self.timeout = timeout
        self.working_dir = working_dir
        self.api_key = api_key
        self.config_path = config_path

        # Verify code is available
        if not self._check_command_available(check_args=["--version"]):
            self.logger.warning(
                "Every Code command not found, some operations may fail",
                extra={"command": self.command},
            )

    @staticmethod
    def _find_available_command(code_command: str, alt_command: str) -> str:
        """
        Find available Every Code command (code or coder).

        Args:
            code_command: Primary command name
            alt_command: Alternative command name

        Returns:
            Available command name
        """

        # Try primary command first
        try:
            result = subprocess.run(
                [code_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 or "--version" in (result.stdout or result.stderr):
                return code_command
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug("Primary command %r not available: %s", code_command, e)
            pass

        # Fall back to alternative command
        try:
            result = subprocess.run(
                [alt_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 or "--version" in (result.stdout or result.stderr):
                return alt_command
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug("Alternative command %r not available: %s", alt_command, e)
            pass

        # Return primary as default (will fail later if not available)
        return code_command

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Every Code command.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        prompt = request.prompt
        context = request.context or {}

        # Build code command input
        code_input = self._build_code_input(prompt, context)

        try:
            # Execute code command using base class method
            result = self._execute_command(input_text=code_input)

            # Build response using base class helper
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "code_success": result.get("success", False),
                    "input_preview": code_input[:200] if len(code_input) > 200 else code_input,
                },
            )

        except AgentTimeoutError as e:
            # Convert timeout to EveryCodeError
            raise EveryCodeError(
                f"Every Code command timed out: {str(e)}",
                command=self.command,
            ) from e
        except AgentError as e:
            # Convert base agent error to EveryCodeError
            raise EveryCodeError(
                f"Every Code command failed: {str(e)}",
                command=self.command,
            ) from e
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            # Convert any other exception to EveryCodeError
            self.logger.error(
                f"Every Code execution failed: {e}",
                exc_info=True,
                extra={"command": self.command, "error": str(e)},
            )
            raise EveryCodeError(f"Every Code command failed: {str(e)}", command=self.command) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Every Code command output.

        Args:
            request: Agent request

        Yields:
            Chunks of output
        """
        prompt = request.prompt
        context = request.context or {}

        code_input = self._build_code_input(prompt, context)

        # Use base class streaming method
        yield from self._stream_command(input_text=code_input)

    def _sanitize_path(self, path_str: str) -> str | None:
        """Sanitize and validate file path."""
        try:
            # Prevent directory traversal / shell injection attempts
            if ".." in path_str or ";" in path_str or "|" in path_str:
                self.logger.warning(f"Suspicious path detected and ignored: {path_str}")
                return None

            path = Path(path_str).resolve()
            # Ensure path exists
            if not path.exists():
                return None

            return str(path)
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(f"Error sanitizing path {path_str}: {e}")
            return None

    def _build_code_input(self, prompt: str, context: dict[str, Any]) -> str:
        """
        Build code command input from prompt and context.

        Args:
            prompt: User prompt
            context: Additional context (may include files, directories, etc.)

        Returns:
            Formatted input string for Every Code CLI
        """
        # Handle special commands (e.g., /plan, /solve, /code, /auto)
        input_parts = []

        # Check if prompt starts with a command
        if prompt.strip().startswith("/"):
            # Pass through commands like /plan, /solve, /code, /auto
            input_parts.append(prompt)
        else:
            # Regular prompt
            input_parts.append(prompt)

        # Handle context parameters
        if "files" in context:
            for file_path in context["files"]:
                sanitized = self._sanitize_path(file_path)
                if sanitized:
                    input_parts.insert(0, f"@{sanitized}\n")

        if "directories" in context:
            for dir_path in context["directories"]:
                sanitized = self._sanitize_path(dir_path)
                if sanitized:
                    input_parts.insert(0, f"@directory {sanitized}\n")

        # Join all parts
        return "\n".join(input_parts)


    def execute_code_command(
        self, command: str, args: list[str] | None = None, input_text: str | None = None
    ) -> dict[str, Any]:
        """
        Execute a code command (e.g., /plan, /solve, /code, /auto).

        Args:
            command: Code command name (e.g., "/plan", "/solve")
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

        return self._execute_command(input_text=cmd_input)

    def get_code_help(self) -> dict[str, Any]:
        """
        Get code help information.

        Returns:
            Help information dictionary
        """
        try:
            result = self._execute_command(args=["--help"], timeout=5)
            return {
                "help_text": result.get("stdout", "") or result.get("stderr", ""),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except (AgentError, ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(
                f"Failed to get Every Code help: {e}",
                extra={"command": self.command, "error": str(e)},
            )
            return {
                "help_text": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

    def get_code_version(self) -> dict[str, Any]:
        """
        Get code version information.

        Returns:
            Version information dictionary
        """
        try:
            result = self._execute_command(args=["--version"], timeout=5)
            return {
                "version": result.get("stdout", "").strip() if result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except (AgentError, ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(
                f"Failed to get Every Code version: {e}",
                extra={"command": self.command, "error": str(e)},
            )
            return {
                "version": None,
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }
