"""HermesClient core — initialization and backend properties."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from codomyrmex.agents.core import AgentCapabilities, AgentRequest, AgentResponse
from codomyrmex.agents.generic import CLIAgentBase
from codomyrmex.agents.hermes.client_pkg.chat import HermesChatMixin
from codomyrmex.agents.hermes.client_pkg.context_memory import HermesContextMixin
from codomyrmex.agents.hermes.client_pkg.errors import HermesError
from codomyrmex.agents.hermes.client_pkg.execution import HermesExecutionMixin
from codomyrmex.agents.hermes.client_pkg.gateway import HermesGatewayMixin
from codomyrmex.agents.hermes.client_pkg.maintenance import HermesMaintenanceMixin
from codomyrmex.agents.hermes.client_pkg.session_ops import HermesSessionOpsMixin


class HermesClient(
    HermesChatMixin,
    HermesContextMixin,
    HermesExecutionMixin,
    HermesGatewayMixin,
    HermesMaintenanceMixin,
    HermesSessionOpsMixin,
    CLIAgentBase,
):
    """Client for interacting with the Hermes Agent."""

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
              - ``fallback_model``  (str | None): fallback model on provider errors
              - ``fallback_provider`` (str | None): fallback provider (e.g. ``"ollama"``)
              - ``hermes_skill_profile_disable`` (bool): skip ``.codomyrmex/hermes_skills_profile.yaml``
              - ``hermes_default_skill_ids`` (list[str] | str): registry ids → CLI ``-s`` names
              - ``hermes_default_hermes_skills`` (list[str] | str): extra raw CLI skill names

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
        timeout = self.get_config_value("timeout", config=cfg) or self.get_config_value(
            "hermes_timeout", config=cfg
        )
        working_dir_str = self.get_config_value("hermes_working_dir", config=cfg)
        self._hermes_provider: str = str(
            self.get_config_value("hermes_provider", config=cfg) or "openrouter"
        )

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

        # Fallback model for provider resilience (v0.2.0)
        self._fallback_model: str | None = self.get_config_value(
            "fallback_model", config=cfg
        )
        self._fallback_provider: str | None = self.get_config_value(
            "fallback_provider", config=cfg
        )

        # CLI flags (v0.2.0+)
        self._yolo: bool = bool(self.get_config_value("yolo", config=cfg))
        self._continue_session: str | None = self.get_config_value(
            "continue_session", config=cfg
        )
        self._pass_session_id: bool = bool(
            self.get_config_value("pass_session_id", config=cfg)
        )

        db_default = Path.home() / ".codomyrmex" / "hermes_sessions.db"
        self._session_db_path = str(
            self.get_config_value("hermes_session_db", config=cfg) or db_default
        )
        Path(self._session_db_path).parent.mkdir(parents=True, exist_ok=True)

        # Worktree isolation config
        self._worktree_base = Path(
            os.path.expanduser(
                str(
                    self.get_config_value("worktree_base_dir", config=cfg)
                    or "~/.codomyrmex/worktrees"
                )
            )
        )

        # Obsidian vault long-term memory config (v1.5.5)
        self._obsidian_vault: str | None = self.get_config_value(
            "obsidian_vault", config=cfg
        )

        # Context compression for long conversations
        from codomyrmex.agents.hermes._provider_router import ContextCompressor

        self._compressor = ContextCompressor(
            max_tokens=self.get_config_value("max_context_tokens", config=cfg)
            or 100_000,
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

        self._skill_profile_disabled: bool = bool(
            self.get_config_value("hermes_skill_profile_disable", config=cfg)
        )
        # Used only during chat_session turns (not thread-safe vs parallel batch on same client).
        self._session_skills_for_next_execute: list[str] | None = None

    @property
    def active_backend(self) -> str:
        """Return the resolved backend name: ``"cli"`` | ``"ollama"`` | ``"none"``."""
        return self._active_backend

    @property
    def ollama_model(self) -> str:
        """Return the configured Ollama model name."""
        return self._ollama_model

__all__ = ["HermesClient"]
