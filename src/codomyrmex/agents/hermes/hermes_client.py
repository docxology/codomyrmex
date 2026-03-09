"""Hermes agent client for Codomyrmex.

Wraps the NousResearch Hermes Agent CLI (``hermes``) for chat completion,
tool-calling pipelines, and skills management.  Falls back to **Ollama**
with the ``hermes3`` model when the CLI binary is not installed.

Backends (configurable via ``hermes_backend``):
- ``"auto"`` (default): use CLI if available, else Ollama
- ``"cli"``: force NousResearch Hermes Agent CLI
- ``"ollama"``: force ``ollama run <model>``
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import AgentError, AgentTimeoutError
from codomyrmex.agents.generic import CLIAgentBase

if TYPE_CHECKING:
    from collections.abc import Iterator


class HermesError(AgentError):
    """Exception raised when Hermes execution fails."""

    def __init__(self, message: str, command: str | None = None) -> None:
        super().__init__(message)
        self.command = command


class HermesClient(CLIAgentBase):
    """Client for interacting with the Hermes Agent.

    Supports two backends:
    - **CLI**: the official NousResearch ``hermes`` binary
    - **Ollama**: ``ollama run hermes3`` (or any configured model)

    The default backend is ``"auto"`` which uses the CLI if available,
    otherwise falls back to Ollama.
    """

    # Default Ollama model for Hermes
    DEFAULT_OLLAMA_MODEL = "hermes3"

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize Hermes client.

        Args:
            config: Optional configuration override.  Recognised keys:

              - ``hermes_command``  (str, default ``"hermes"``): CLI binary path
              - ``hermes_timeout``  (int, default 120): subprocess timeout (s)
              - ``hermes_working_dir`` (str | None): working directory
              - ``hermes_backend``  (str, default ``"auto"``): ``"auto"`` | ``"cli"`` | ``"ollama"``
              - ``hermes_model``    (str, default ``"hermes3"``): Ollama model name
        """
        cfg = config or {}
        super().__init__(
            name="hermes",
            command="hermes",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
            ],
            config=cfg,
            timeout=120,
            working_dir=None,
        )

        hermes_command = self.get_config_value("hermes_command", config=cfg)
        timeout = self.get_config_value("hermes_timeout", config=cfg)
        working_dir_str = self.get_config_value("hermes_working_dir", config=cfg)

        if hermes_command:
            self.command = hermes_command
        if timeout is not None:
            self.timeout = timeout
        if working_dir_str:
            self.working_dir = Path(working_dir_str)

        # Backend selection
        self._backend: str = str(
            self.get_config_value("hermes_backend", config=cfg) or "auto"
        ).lower()
        self._ollama_model: str = str(
            self.get_config_value("hermes_model", config=cfg)
            or self.DEFAULT_OLLAMA_MODEL
        )

        # Probe availability
        self._cli_available = self._check_command_available(check_args=["version"])
        self._ollama_available = bool(shutil.which("ollama"))

        if self._backend == "auto":
            if self._cli_available:
                self._active_backend = "cli"
            elif self._ollama_available:
                self._active_backend = "ollama"
                self.logger.info(
                    "Hermes CLI not found — using Ollama backend with model '%s'",
                    self._ollama_model,
                )
            else:
                self._active_backend = "none"
                self.logger.warning(
                    "Neither hermes CLI nor ollama found. Operations will fail."
                )
        else:
            self._active_backend = self._backend

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def active_backend(self) -> str:
        """Return the resolved backend name: ``"cli"`` | ``"ollama"`` | ``"none"``."""
        return self._active_backend

    @property
    def ollama_model(self) -> str:
        """Return the configured Ollama model name."""
        return self._ollama_model

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute via the active backend (CLI or Ollama)."""
        if self._active_backend == "ollama":
            return self._execute_via_ollama(request)
        return self._execute_via_cli(request)

    def _execute_via_cli(self, request: AgentRequest) -> AgentResponse:
        """Execute via the NousResearch Hermes CLI."""
        prompt = request.prompt
        context = request.context or {}
        hermes_args = self._build_hermes_args(prompt, context)

        try:
            result = self._execute_command(args=hermes_args)
            if not result.get("success", False):
                raise HermesError(
                    f"Hermes CLI failed (exit {result.get('exit_code')}):\n"
                    f"{result.get('stderr') or result.get('stdout')}",
                    command=self.command,
                )
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "backend": "cli",
                    "command_full": " ".join([self.command, *hermes_args]),
                },
            )
        except AgentTimeoutError as e:
            raise HermesError(
                f"Hermes CLI timed out after {self.timeout}s: {e}", command=self.command
            ) from e
        except AgentError as e:
            raise HermesError(f"Hermes CLI failed: {e}", command=self.command) from e
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Hermes CLI execution failed: %s", e, exc_info=True)
            raise HermesError(f"Hermes CLI failed: {e}", command=self.command) from e

    def _execute_via_ollama(self, request: AgentRequest) -> AgentResponse:
        """Execute via ``ollama run <model>``."""
        ollama_bin = shutil.which("ollama") or "ollama"
        prompt = request.prompt
        cmd = [ollama_bin, "run", self._ollama_model, prompt]

        self.logger.info(
            "Hermes via Ollama: model=%s, prompt=%s…", self._ollama_model, prompt[:60]
        )
        start = time.time()

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**__import__("os").environ, "NO_COLOR": "1"},
            )
            elapsed = time.time() - start
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            success = proc.returncode == 0 and bool(stdout)

            if not success:
                raise HermesError(
                    f"Ollama hermes3 failed (exit {proc.returncode}): {stderr or stdout}",
                    command=" ".join(cmd),
                )

            return AgentResponse(
                content=stdout,
                error=None,
                metadata={
                    "backend": "ollama",
                    "model": self._ollama_model,
                    "exit_code": proc.returncode,
                    "command": " ".join(cmd),
                },
                execution_time=elapsed,
            )

        except subprocess.TimeoutExpired:
            raise HermesError(
                f"Ollama timed out after {self.timeout}s", command=" ".join(cmd)
            ) from None
        except HermesError:
            raise
        except Exception as e:
            self.logger.error("Ollama execution failed: %s", e, exc_info=True)
            raise HermesError(
                f"Ollama execution failed: {e}", command=" ".join(cmd)
            ) from e

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream output from the active backend."""
        if self._active_backend == "ollama":
            yield from self._stream_via_ollama(request)
        else:
            prompt = request.prompt
            context = request.context or {}
            hermes_args = self._build_hermes_args(prompt, context)
            yield from self._stream_command(args=hermes_args)

    def _stream_via_ollama(self, request: AgentRequest) -> Iterator[str]:
        """Stream output from ``ollama run <model>``."""
        ollama_bin = shutil.which("ollama") or "ollama"
        cmd = [ollama_bin, "run", self._ollama_model, request.prompt]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env={**__import__("os").environ, "NO_COLOR": "1"},
            )
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield line.rstrip()
            process.wait(timeout=self.timeout)
        except Exception as e:
            self.logger.error("Ollama streaming failed: %s", e, exc_info=True)
            yield f"Error: {e}"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_hermes_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """Build hermes CLI arguments from prompt and context.

        Args:
            prompt: Text prompt or task description.
            context: Context dictionary which may include keys:
                - ``command``: Subcommand (e.g. ``"skills"``, ``"setup"``)
                - ``args``: Additional arguments for the subcommand

        Returns:
            Argument list suitable for subprocess call.
        """
        if context.get("command"):
            cmd = context["command"]
            args = [cmd]
            if context.get("args"):
                args.extend(context["args"])
            return args
        return ["chat", "-q", prompt]

    # ------------------------------------------------------------------
    # Skills / Status (CLI-only — graceful fallback)
    # ------------------------------------------------------------------

    def list_skills(self) -> dict[str, Any]:
        """List active skills available to Hermes.

        Returns:
            Dict with ``success`` boolean and ``output`` or ``error``.
        """
        if self._active_backend != "cli":
            return {"success": False, "error": "Skills listing requires the Hermes CLI"}
        try:
            result = self._execute_command(args=["skills", "list"])
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
            }
        except Exception as e:
            self.logger.warning("Failed to list Hermes skills: %s", e)
            return {"success": False, "error": str(e)}

    def get_hermes_status(self) -> dict[str, Any]:
        """Get the current Hermes configuration status.

        Returns:
            Dict with diagnostic information including the active backend.
        """
        status: dict[str, Any] = {
            "active_backend": self._active_backend,
            "cli_available": self._cli_available,
            "ollama_available": self._ollama_available,
            "ollama_model": self._ollama_model,
        }
        if self._active_backend == "cli":
            try:
                result = self._execute_command(args=["status"], timeout=10)
                status.update(
                    {
                        "success": result.get("success", False),
                        "output": result.get("stdout", ""),
                        "exit_code": result.get("exit_code", 0),
                    }
                )
            except Exception as e:
                status.update({"success": False, "error": str(e), "exit_code": -1})
        else:
            status["success"] = self._ollama_available
        return status
