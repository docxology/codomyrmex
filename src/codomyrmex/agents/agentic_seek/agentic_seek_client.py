"""agenticSeek CLI client for Codomyrmex agents.

Wraps the `agenticSeek <https://github.com/Fosowl/agenticSeek>`_
framework as a ``CLIAgentBase`` agent, providing subprocess-based
invocation, ``config.ini`` parsing, and environment validation.

Reference: https://github.com/Fosowl/agenticSeek
"""

from __future__ import annotations

import configparser
import os
import shutil
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any


from codomyrmex.agents.agentic_seek.agent_router import AgenticSeekRouter
from codomyrmex.agents.agentic_seek.agent_types import (
    AgenticSeekAgentType,
    AgenticSeekConfig,
)
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import AgentError
from codomyrmex.agents.generic.cli_agent_base import CLIAgentBase
from codomyrmex.config_management.defaults import (
    DEFAULT_API_BASE_URL,
    DEFAULT_OLLAMA_URL,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger
logger = get_logger(__name__)


class AgenticSeekClient(CLIAgentBase):
    """Client for the agenticSeek autonomous agent framework.

    agenticSeek is a fully-local alternative to Manus AI that
    autonomously browses the web, writes and executes code, and
    plans complex multi-step tasks—all running on local hardware.

    This client integrates as a ``CLIAgentBase`` and provides:

    * CLI invocation via ``uv run cli.py``
    * Docker-based invocation via ``docker compose``
    * ``config.ini`` reading and writing
    * Environment health checks (Docker, Ollama, SearxNG)
    * Heuristic agent routing
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialise the agenticSeek client.

        Args:
            config: Optional configuration overrides.  Supports keys
                such as ``agentic_seek_path`` (path to the cloned repo)
                and ``agentic_seek_docker`` (``True`` to use Docker).
        """
        _cfg = config or {}
        repo_path = _cfg.get("agentic_seek_path", "")

        super().__init__(
            name="agentic_seek",
            command="uv run cli.py",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.MULTI_TURN,
            ],
            config=config,
            timeout=_cfg.get("agentic_seek_timeout", 300),
            working_dir=Path(repo_path) if repo_path else None,
        )
        self._config = _cfg
        self._repo_path: str = repo_path
        self._use_docker: bool = self._config.get(
            "agentic_seek_docker", True
        )
        self._router = AgenticSeekRouter()
        self._seek_config: AgenticSeekConfig | None = None

    # ------------------------------------------------------------------ #
    # CLIAgentBase overrides
    # ------------------------------------------------------------------ #

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute an agenticSeek request via subprocess.

        Sends the prompt to the agenticSeek CLI (or Docker backend)
        and captures the full output.

        Args:
            request: The agent request containing the user prompt.

        Returns:
            Structured ``AgentResponse``.
        """
        start_time = time.time()
        cmd = self._build_command(request.prompt)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._config.get("agentic_seek_timeout", 300),
                cwd=self._repo_path or None,
            )
            execution_time = time.time() - start_time
            content = result.stdout.strip()
            if result.returncode != 0 and result.stderr:
                content += f"\n\n--- stderr ---\n{result.stderr.strip()}"

            return self._build_agent_response(
                content=content,
                metadata={
                    "returncode": result.returncode,
                    "agent_type": self._router.classify_query(
                        request.prompt
                    ).value,
                },
                execution_time=execution_time,
            )
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            raise AgentError(
                f"agenticSeek timed out after {execution_time:.1f}s"
            ) from None
        except FileNotFoundError as exc:
            execution_time = time.time() - start_time
            raise AgentError(
                f"agenticSeek CLI not found: {exc}"
            ) from exc

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream agenticSeek output line by line.

        Args:
            request: The agent request.

        Yields:
            Lines of output from the subprocess.
        """
        cmd = self._build_command(request.prompt)
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self._repo_path or None,
            )
            if proc.stdout is not None:
                for line in proc.stdout:
                    yield line.rstrip("\n")
            proc.wait()
        except FileNotFoundError as exc:
            yield f"Error: agenticSeek CLI not found: {exc}"

    # ------------------------------------------------------------------ #
    # Public helpers
    # ------------------------------------------------------------------ #

    def get_available_agents(self) -> list[AgenticSeekAgentType]:
        """Return the list of agent types available in agenticSeek.

        Returns:
            All ``AgenticSeekAgentType`` members (the upstream project
            always ships all five agent types).
        """
        return list(AgenticSeekAgentType)

    def classify_query(self, query: str) -> AgenticSeekAgentType:
        """Classify which agent type would handle a given query.

        Args:
            query: User prompt text.

        Returns:
            The recommended agent type.
        """
        return self._router.classify_query(query)

    def get_agent_status(self) -> dict[str, Any]:
        """Check the health of the agenticSeek backend.

        Returns a dict with keys:

        * ``"backend_running"`` – whether the Docker backend is reachable
        * ``"repo_path"`` – configured repository path
        * ``"docker_available"`` – whether ``docker`` CLI is found
        """
        return {
            "backend_running": self._check_backend_health(),
            "repo_path": self._repo_path,
            "docker_available": shutil.which("docker") is not None,
        }

    def validate_environment(self) -> dict[str, bool]:
        """Validate external dependencies required by agenticSeek.

        Returns:
            Dict mapping dependency names to availability booleans.
        """
        return {
            "docker": shutil.which("docker") is not None,
            "docker_compose": _check_docker_compose(),
            "ollama": shutil.which("ollama") is not None,
            "python": shutil.which("python3") is not None,
            "uv": shutil.which("uv") is not None,
            "repo_exists": bool(
                self._repo_path and Path(self._repo_path).is_dir()
            ),
        }

    @staticmethod
    def parse_config_ini(path: str) -> AgenticSeekConfig:
        """Parse an agenticSeek ``config.ini`` into a typed config.

        Args:
            path: Path to the ``config.ini`` file.

        Returns:
            Populated ``AgenticSeekConfig`` dataclass.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If required sections are missing.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        parser = configparser.ConfigParser()
        parser.read(path)

        if "MAIN" not in parser:
            raise ValueError("config.ini missing [MAIN] section")

        main = parser["MAIN"]
        browser = parser["BROWSER"] if "BROWSER" in parser else {}

        def _bool(val: str) -> bool:
            return val.strip().lower() in ("true", "1", "yes")

        languages_raw = main.get("languages", "en")
        languages = [
            lang.strip()
            for lang in languages_raw.replace(",", " ").split()
            if lang.strip()
        ]

        return AgenticSeekConfig(
            is_local=_bool(main.get("is_local", "True")),
            provider_name=main.get("provider_name", "ollama"),
            provider_model=main.get("provider_model", "deepseek-r1:14b"),
            provider_server_address=main.get(
                "provider_server_address",
                os.getenv("AGENTIC_SEEK_PROVIDER_URL", DEFAULT_OLLAMA_URL),
            ),
            agent_name=main.get("agent_name", "Friday"),
            recover_last_session=_bool(
                main.get("recover_last_session", "False")
            ),
            save_session=_bool(main.get("save_session", "False")),
            speak=_bool(main.get("speak", "False")),
            listen=_bool(main.get("listen", "False")),
            work_dir=main.get("work_dir", ""),
            jarvis_personality=_bool(
                main.get("jarvis_personality", "False")
            ),
            languages=languages,
            headless_browser=_bool(
                browser.get("headless_browser", "True")
            ),
            stealth_mode=_bool(browser.get("stealth_mode", "True")),
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _build_command(self, prompt: str) -> list[str]:
        """Build the subprocess command for executing a prompt."""
        if self._use_docker:
            return [
                "docker", "compose", "exec", "backend",
                "python", "-c",
                f'from sources.interaction import Interaction; '
                f'print(Interaction.quick_query("{_escape(prompt)}"))',
            ]
        return ["uv", "run", "cli.py"]

    def _check_backend_health(self) -> bool:
        """Ping the backend health endpoint."""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 f"{os.getenv('AGENTIC_SEEK_BACKEND_URL', DEFAULT_API_BASE_URL)}/health"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() == "200"
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning("Backend health check failed: %s", e)
            return False


# ---------------------------------------------------------------------------
# Module-private helpers
# ---------------------------------------------------------------------------

def _escape(text: str) -> str:
    """Escape a string for embedding in a Python f-string command."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")


def _check_docker_compose() -> bool:
    """Check if ``docker compose`` (V2) is available."""
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.warning("Docker compose availability check failed: %s", e)
        return False
