import json
import shutil
import subprocess
from collections.abc import Iterator
from typing import Any

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GeminiCLIWrapper(BaseAgent):
    """Client for interacting with the gemini CLI package (gemini-cli)."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Execute   Init   operations natively."""
        super().__init__(
            name="gemini_cli",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
            ],
            config=config or {},
        )

        self.cli_path = shutil.which("gemini")
        self.default_model = self.get_config_value("gemini_model", default=None, config=config)

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute  Execute Impl operations natively."""
        if not self.cli_path:
            raise GeminiError("gemini CLI executable not found")

        prompt = request.prompt
        context = request.context or {}
        model = context.get("model", self.default_model)

        cmd = [self.cli_path]
        
        # Add basic prompt
        if prompt:
            cmd.append(prompt)

        # Output format json
        cmd.extend(["--output-format", "json"])

        if model:
            cmd.extend(["--model", model])

        # Additional options from context
        if "sandbox" in context and context["sandbox"]:
            cmd.append("--sandbox")
            
        if "yolo" in context and context["yolo"]:
            cmd.append("--yolo")
            
        if "extensions" in context:
            cmd.append("--extensions")
            cmd.extend(context["extensions"])
            
        if "include_directories" in context:
            cmd.append("--include-directories")
            cmd.extend(context["include_directories"])

        try:
            logger.debug(f"Executing gemini CLI command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                # Sometimes the CLI writes error to stdout instead of stderr depending on how it's handled
                error_msg = result.stderr.strip() or result.stdout.strip()
                raise GeminiError(f"Gemini CLI execution failed with code {result.returncode}: {error_msg}")

            # Attempt to parse json
            content = result.stdout.strip()
            parsed_json = {}
            try:
                parsed_json = json.loads(content)
                # The structured metadata might give us specific fields
                actual_content = parsed_json.get("text", content)
            except json.JSONDecodeError:
                actual_content = content

            return AgentResponse(
                request_id=request.id,
                content=actual_content,
                metadata={
                    "model": model,
                    "raw": parsed_json,
                }
            )

        except subprocess.SubprocessError as e:
            raise GeminiError(f"Failed to execute gemini CLI: {e}") from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Execute  Stream Impl operations natively."""
        # CLI streaming is complex. We will implement simple blocking execution for now
        # and yield it as a single chunk.
        logger.warning("Streaming is not fully supported via CLI subprocess. Falling back to block execute.")
        try:
            response = self._execute_impl(request)
            yield response.content
        except Exception as e:
            logger.error(f"Gemini CLI streaming failed: {e}")
            yield f"\n[Error: {e}]"

    # --- CLI specific methods ---

    def list_sessions(self) -> str:
        """List available sessions for the current project."""
        if not self.cli_path:
            raise GeminiError("gemini CLI executable not found")

        cmd = [self.cli_path, "--list-sessions"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GeminiError(f"Failed to list sessions: {e}") from e

    def delete_session(self, session_identifier: str) -> str:
        """Delete a session by index number."""
        if not self.cli_path:
            raise GeminiError("gemini CLI executable not found")

        cmd = [self.cli_path, "--delete-session", str(session_identifier)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GeminiError(f"Failed to delete session {session_identifier}: {e}") from e

    def list_extensions(self) -> str:
        """List all available extensions."""
        if not self.cli_path:
            raise GeminiError("gemini CLI executable not found")

        cmd = [self.cli_path, "--list-extensions"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GeminiError(f"Failed to list extensions: {e}") from e

    def manage_mcp(self, mcp_args: list[str]) -> str:
        """Manage MCP servers (e.g. ['list'], ['add', 'server_name', '...'])"""
        if not self.cli_path:
            raise GeminiError("gemini CLI executable not found")

        cmd = [self.cli_path, "mcp"] + mcp_args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GeminiError(f"Failed to manage mcp with args {mcp_args}: {e}") from e

    def manage_extensions(self, ext_args: list[str]) -> str:
        """Manage Gemini CLI extensions."""
        if not self.cli_path:
            raise GeminiError("gemini CLI executable not found")

        cmd = [self.cli_path, "extensions"] + ext_args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GeminiError(f"Failed to manage extensions with args {ext_args}: {e}") from e
