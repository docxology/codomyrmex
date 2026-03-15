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

import os
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
from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

if TYPE_CHECKING:
    from collections.abc import Iterator

# Packages allowed for automatic installation by the auto-heal system.
# Only these well-known, commonly-safe packages may be installed without
# explicit user approval.
AUTO_HEAL_ALLOWLIST: set[str] = {
    "requests",
    "numpy",
    "pandas",
    "httpx",
    "pydantic",
    "rich",
    "click",
    "psutil",
    "pillow",
    "cryptography",
    "pyyaml",
    "toml",
    "jinja2",
    "sqlalchemy",
    "redis",
    "celery",
    "fastapi",
    "uvicorn",
    "gunicorn",
    "flask",
    "boto3",
    "paramiko",
    "websockets",
    "aiohttp",
    "beautifulsoup4",
    "lxml",
}


class HermesError(AgentError):
    """Exception raised when Hermes execution fails."""

    def __init__(self, message: str, command: str | None = None) -> None:
        super().__init__(message)
        self.command = command


class AutoRetryException(Exception):
    """Exception raised internally to trigger the autonomous error-correction loop."""


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
              - ``fallback_model``  (str | None): fallback model on provider errors
              - ``fallback_provider`` (str | None): fallback provider (e.g. ``"ollama"``)
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
            max_tokens=int(
                self.get_config_value("max_context_tokens", config=cfg) or 100_000
            ),
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

    def _is_cli_configured(self) -> bool:
        """Check whether the Hermes CLI has an API key configured.

        Checks two sources:
        1. ``hermes config`` output — looks for API key lines that show
           actual key values (not ``(not set)``).
        2. ``~/.hermes/.env`` — scans for a non-empty ``OPENROUTER_API_KEY=``.

        Returns:
            True if at least one API key is configured.
        """
        # Method 1: check `hermes config` output
        try:
            result = subprocess.run(
                [self.command, "config"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = result.stdout + result.stderr
            # Parse the "◆ API Keys" section — each line looks like:
            #   OpenRouter     sk-o...fa72      (configured)
            #   Anthropic      (not set)        (not configured)
            key_providers = [
                "openrouter",
                "anthropic",
                "openai",
                "zhipuai",
                "glm",
                "kimi",
            ]
            for line in output.splitlines():
                lower_line = line.strip().lower()
                for provider in key_providers:
                    if (
                        lower_line.startswith(provider)
                        and "(not set)" not in lower_line
                    ):
                        # Found a provider line with an actual key value
                        return True
        except Exception as exc:
            self.logger.debug("Failed to parse `hermes config` output: %s", exc)  # Fall through to .env check

        # Method 2: check ~/.hermes/.env directly
        try:
            hermenv = os.path.expanduser("~/.hermes/.env")
            if os.path.exists(hermenv):
                with open(hermenv) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("OPENROUTER_API_KEY=") and len(line) > len(
                            "OPENROUTER_API_KEY="
                        ):
                            return True
        except Exception as exc:
            self.logger.debug("Failed to read ~/.hermes/.env: %s", exc)

        # Method 3: check environment variable
        if os.environ.get("OPENROUTER_API_KEY"):
            return True

        return False

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute via the active backend, with fallback on provider errors."""
        try:
            return self._execute_primary(request)
        except HermesError as exc:
            if self._fallback_model and self._should_fallback(exc):
                self.logger.warning(
                    "Primary provider failed (%s) — retrying with fallback model '%s'",
                    exc,
                    self._fallback_model,
                )
                return self._execute_via_ollama(
                    request, model_override=self._fallback_model
                )
            raise

    def _execute_primary(self, request: AgentRequest) -> AgentResponse:
        """Execute via the primary active backend (CLI or Ollama)."""
        if self._active_backend == "ollama":
            return self._execute_via_ollama(request)
        if not self._is_cli_configured():
            self.logger.warning(
                "Hermes CLI has no API key configured — falling back to Ollama. "
                "Run 'hermes setup' in your terminal to configure an API key."
            )
            return self._execute_via_ollama(request)
        return self._execute_via_cli(request)

    @staticmethod
    def _should_fallback(exc: HermesError) -> bool:
        """Determine if the error warrants a fallback retry.

        Returns True for 413 (payload too large), rate limits, and timeouts.
        """
        msg = str(exc).lower()
        return any(
            pattern in msg
            for pattern in (
                "413",
                "payload too large",
                "rate limit",
                "timed out",
                "timeout",
                "429",
                "too many requests",
                "quota",
                "capacity",
            )
        )

    def _execute_via_cli(self, request: AgentRequest) -> AgentResponse:
        """Execute via the NousResearch Hermes CLI."""
        prompt = request.prompt
        context = request.context or {}
        hermes_args = self._build_hermes_args(prompt, context)

        try:
            # Build environment for the subprocess: inherit os.environ and
            # add any API key vars needed by the hermes CLI so it doesn't
            # enter interactive setup mode.
            subprocess_env = dict(os.environ)
            for key_name in (
                "OPENROUTER_API_KEY",
                "HERMES_INFERENCE_PROVIDER",
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
            ):
                if key_name not in subprocess_env:
                    # Try loading from ~/.hermes/.env
                    hermenv = os.path.expanduser("~/.hermes/.env")
                    if os.path.exists(hermenv):
                        with open(hermenv) as f:
                            for line in f:
                                line = line.strip()
                                if (
                                    line.startswith(f"{key_name}=")
                                    and len(line) > len(key_name) + 1
                                ):
                                    subprocess_env[key_name] = line.split("=", 1)[1]
                                    break
            subprocess_env["NO_COLOR"] = "1"

            result = self._execute_command(args=hermes_args, env=subprocess_env)
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

    def _execute_via_ollama(
        self,
        request: AgentRequest,
        *,
        model_override: str | None = None,
    ) -> AgentResponse:
        """Execute via ``ollama run <model>``.

        Args:
            request: Agent request to execute.
            model_override: Override the default Ollama model (used by fallback).
        """
        ollama_bin = shutil.which("ollama") or "ollama"
        model = model_override or self._ollama_model
        prompt = request.prompt
        cmd = [ollama_bin, "run", model, prompt]

        self.logger.info("Hermes via Ollama: model=%s, prompt=%s…", model, prompt[:60])
        start = time.time()

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, "NO_COLOR": "1"},
            )
            elapsed = time.time() - start
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            success = proc.returncode == 0 and bool(stdout)

            if not success:
                raise HermesError(
                    f"Ollama {model} failed (exit {proc.returncode}): {stderr or stdout}",
                    command=" ".join(cmd),
                )

            return AgentResponse(
                content=stdout,
                error=None,
                metadata={
                    "backend": "ollama",
                    "model": model,
                    "exit_code": proc.returncode,
                    "command": " ".join(cmd),
                    "is_fallback": model_override is not None,
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
                env={**os.environ, "NO_COLOR": "1"},
            )
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield line.rstrip()
            process.wait(timeout=self.timeout)
        except Exception as e:
            self.logger.error("Ollama streaming failed: %s", e, exc_info=True)
            yield f"Error: {e}"

    # ------------------------------------------------------------------
    # Sessions (Multi-turn Chat)
    # ------------------------------------------------------------------

    def _summarize_context(self, session: Any) -> None:
        """Summarize and archive the oldest half of the session's messages."""
        messages = session.messages
        half = len(messages) // 2
        if half < 2:
            return

        oldest = messages[:half]
        latest = messages[half:]

        hist_text = ""
        for m in oldest:
            hist_text += f"[{m['role'].upper()}]\n{m['content']}\n\n"

        # 1. Pipeline Summary
        summary_prompt = (
            "Summarize the core facts, exact constraints, and key context from the following "
            "conversation excerpt securely. Format your output strictly as a dense timeline or list.\n\n"
            f"<EXCERPT>\n{hist_text}\n</EXCERPT>"
        )

        from codomyrmex.agents.core import AgentRequest

        self.logger.info(
            "Triggering context summarization for session %s (compressing %d messages)",
            session.session_id,
            len(oldest),
        )
        summary_resp = self.execute(AgentRequest(prompt=summary_prompt))
        summary = (
            summary_resp.content
            if summary_resp.is_success()
            else "(Summarization failed)"
        )

        # 2. Fact Extraction
        fact_prompt = (
            "Extract any permanent user preferences, structural facts, or environmental constraints "
            "from this excerpt. Return ONLY a bulleted list of facts, nothing else. If none, return exactly 'NONE'.\n\n"
            f"<EXCERPT>\n{hist_text}\n</EXCERPT>"
        )
        fact_resp = self.execute(AgentRequest(prompt=fact_prompt))
        if fact_resp.is_success() and "NONE" not in fact_resp.content.strip().upper():
            existing_facts = session.metadata.get("extracted_facts", "")
            session.metadata["extracted_facts"] = (
                existing_facts + "\n" + fact_resp.content.strip()
            ).strip()

        # Fold existing summary if present into the new one (if the first message is already a summary)
        if (
            oldest
            and oldest[0].get("role") == "system"
            and "<SESSION_SUMMARY>" in oldest[0].get("content", "")
        ):
            prior_summary = (
                oldest[0]["content"]
                .replace("<SESSION_SUMMARY>", "")
                .replace("</SESSION_SUMMARY>", "")
                .strip()
            )
            summary = f"{prior_summary}\n\n[Continuance]:\n{summary}"

        # 3. Automated Graph Link Inference
        graph_prompt = (
            "You are an Obsidian notes semantic linker. Take the following summary text and strictly "
            "wrap any core architectural concepts, languages, frameworks, or significant domain entities "
            "with Obsidian-style double brackets (e.g., [[Concept]]). Do not change the text other than adding brackets. "
            f"Here is the text:\n\n{summary}"
        )
        graph_resp = self.execute(AgentRequest(prompt=graph_prompt))
        if graph_resp.is_success():
            summary = graph_resp.content.strip()

        summary_msg = {
            "role": "system",
            "content": f"<SESSION_SUMMARY>\n{summary}\n</SESSION_SUMMARY>",
        }
        session.messages = [summary_msg, *latest]

        # 4. Export to Obsidian natively
        self._export_to_obsidian(
            session_id=session.session_id, name=session.name, content=summary
        )

    def _export_to_obsidian(
        self, session_id: str, name: str | None, content: str
    ) -> None:
        """Export a semantic session summary to the Obsidian Vault if configured."""
        try:
            import os
            from pathlib import Path

            from codomyrmex.agentic_memory.obsidian.crud import create_note
            from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault

            # Use configured vault path if set, otherwise discover in workspace
            if self._obsidian_vault:
                vault_path = Path(os.path.expanduser(self._obsidian_vault)).resolve()
            else:
                workspace_root = Path(os.path.abspath(".")).resolve()
                vault_path = workspace_root / "docs" / "brain"

            # If the vault exists, write natively
            if vault_path.exists() and vault_path.is_dir():
                vault = ObsidianVault(vault_path)
                safe_title = (
                    (name or f"session-{session_id}")[:50]
                    .replace("/", "-")
                    .replace("\\", "-")
                )
                note_path = f"Sessions/{safe_title}.md"
                fm = {
                    "agentic_id": session_id,
                    "importance": "high",
                    "memory_type": "semantic",
                    "source": "hermes_context_compression",
                }
                create_note(vault, note_path, content=content, frontmatter=fm)
                self.logger.info(
                    "Exported session %s context to Obsidian Vault: %s",
                    session_id,
                    note_path,
                )
        except Exception as e:
            self.logger.warning("Failed to export summary to Obsidian: %s", e)

    def chat_session(
        self,
        prompt: str,
        session_id: str | None = None,
        session_name: str | None = None,
    ) -> AgentResponse:
        """Execute a stateful multi-turn chat.

        Args:
            prompt: User prompt.
            session_id: Session ID (optional). If omitted, a new one is created.
            session_name: Human-friendly session name (v0.2.0). If provided and
                no session_id is given, attempts to resume by name.

        Returns:
            Response containing the assistant's reply and the session ID in metadata.
        """
        with SQLiteSessionStore(self._session_db_path) as store:
            # Try to resolve session by name first (v0.2.0 feature)
            if not session_id and session_name:
                existing = store.find_by_name(session_name)
                if existing:
                    session = existing
                    session_id = session.session_id
                else:
                    session = HermesSession(name=session_name)
                    session_id = session.session_id
            elif session_id:
                session = store.load(session_id)
                if not session:
                    session = HermesSession(session_id=session_id, name=session_name)
            else:
                session = HermesSession(name=session_name)
                session_id = session.session_id

            # Update name if provided on an existing session
            if session_name and session.name != session_name:
                session.name = session_name

            store.save(session)

            current_prompt = prompt
            role = "user"
            autonomous_turns = 0
            max_turns = 10
            final_response = None

            while autonomous_turns < max_turns:
                session.add_message(role, current_prompt)

                max_session_msgs = self.config.get("max_session_messages", 20)
                if len(session.messages) > max_session_msgs:
                    self._summarize_context(session)
                    store.save(session)

                # Auto-compress history if it exceeds token limits
                history_messages = session.messages[:-1]  # exclude the current prompt
                if self._compressor.needs_compression(history_messages):
                    history_messages = self._compressor.compress(history_messages)
                    self.logger.info(
                        "Session %s: compressed %d → %d history messages",
                        session.session_id,
                        len(session.messages) - 1,
                        len(history_messages),
                    )

                # Build full prompt containing history
                history_text = ""
                for msg in history_messages:
                    history_text += f"[{msg['role'].upper()}]\n{msg['content']}\n\n"

                system_directives = (
                    f"You are the Hermes agent. Your current session ID is '{session.session_id}'.\n"
                    "For complex, multi-step requests, you MUST break them down into an internal checklist "
                    "using the `hermes_create_task` and `hermes_update_task_status` MCP tools. "
                    "Create tasks first, then execute them iteratively. Update their status to 'completed' or 'failed' as you go."
                )

                if history_text:
                    extra_facts = ""
                    extracted_facts = session.metadata.get("extracted_facts", "")
                    if extracted_facts:
                        extra_facts = f"\n\nRetained Long-Term Facts / Preferences:\n{extracted_facts}\n"

                    full_prompt = (
                        f"{system_directives}{extra_facts}\n\n"
                        f"Previous Conversation:\n{history_text}"
                        f"[{session.messages[-1]['role'].upper()}]\n{current_prompt}\n\n"
                        f"Please respond."
                    )
                else:
                    full_prompt = f"{system_directives}\n\nUser: {current_prompt}"

                request = AgentRequest(prompt=full_prompt)
                response = self.execute(request)
                final_response = response

                if response.is_success():
                    # Reload session FIRST to get latest metadata changes from MCP tools
                    latest_session = store.load(session_id)
                    if latest_session:
                        session.metadata = latest_session.metadata

                    session.add_message("assistant", response.content)
                    store.save(session)

                    tasks = session.metadata.get("workflow_tasks", {})

                    has_pending = any(
                        t.get("status") in ("pending", "running")
                        for t in tasks.values()
                    )
                    if has_pending:
                        autonomous_turns += 1
                        current_prompt = "System: You have pending tasks in your workflow checklist. Please execute the next logical task, use necessary tools, and update its status when done."
                        role = "user"
                    else:
                        break  # All tasks completed, or no tasks created
                else:
                    exit_code = response.metadata.get("exit_code", 0)
                    if exit_code != 0 and autonomous_turns < max_turns:
                        autonomous_turns += 1
                        error_trace = response.error or response.metadata.get(
                            "stderr", "Unknown error"
                        )

                        # 1.5.13 Dependency Healing Interception
                        import re

                        missing_pkg_match = re.search(
                            r"(?:ModuleNotFoundError|ImportError): No module named '([^']+)'",
                            error_trace,
                        )
                        if missing_pkg_match:
                            missing_pkg = missing_pkg_match.group(1)
                            self.logger.warning(
                                f"Detected missing dependency '{missing_pkg}'. Initiating autonomous healing."
                            )
                            heal_result = self._heal_environment(missing_pkg)

                            attempts = session.metadata.get("heal_attempts", 0) + 1
                            session.metadata["heal_attempts"] = attempts
                            successes = session.metadata.get("heal_success_rate", 0)
                            if heal_result["success"]:
                                session.metadata["heal_success_rate"] = successes + 1

                            error_trace += f"\n\n[SYSTEM AUTO-HEAL]: Attempted to install missing package '{missing_pkg}'. Result: {heal_result['output']}"

                        self.logger.warning(
                            "Subprocess execution failed (exit_code=%s). Initiating recovery loop via AutoRetryException logic.",
                            exit_code,
                        )

                        template_path = (
                            Path(__file__).parent / "templates" / "recovery_prompt.txt"
                        )
                        if template_path.exists():
                            recovery_text = template_path.read_text(
                                encoding="utf-8"
                            ).format(failed_trace=error_trace)
                        else:
                            recovery_text = f"System: Tool failed with trace:\n<FAILED_TRACE>\n{error_trace}\n</FAILED_TRACE>\nFix the error and proceed."

                        if response.content:
                            session.add_message(
                                "assistant",
                                f"{response.content}\n[Execution Interrupted]",
                            )

                        current_prompt = recovery_text
                        role = "system"
                        # Reload session to ensure we don't drop state
                        store.save(session)
                        continue
                    break  # Error executing, and we are out of retry turns

            # Sync securely to Obsidian Vault if configured (D1 implementation)
            if self._obsidian_vault and final_response and final_response.is_success():
                try:
                    from codomyrmex.agents.hermes.gateway.memory import (
                        sync_session_to_vault,
                    )

                    sync_session_to_vault(session, self._obsidian_vault)
                except Exception as e:
                    self.logger.error("Error executing vault sync hook: %s", e)

            if final_response:
                final_response.metadata["session_id"] = session.session_id
                if session.name:
                    final_response.metadata["session_name"] = session.name
                final_response.metadata["workflow_tasks"] = session.metadata.get(
                    "workflow_tasks", {}
                )
                final_response.metadata["autonomous_turns"] = autonomous_turns
                return final_response

            from codomyrmex.agents.core import AgentResponse

            return AgentResponse(content="", error="Execution loop failed", metadata={})

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
        # Non-interactive mode: -Q suppresses spinner/banner, --provider forces the
        # configured inference provider so hermes never enters the setup wizard.
        args = ["chat", "-q", prompt, "-Q", "--provider", self._hermes_provider]
        if self._yolo:
            args.append("--yolo")
        if self._continue_session:
            args.extend(["--continue", self._continue_session])
        if self._pass_session_id:
            args.append("--pass-session-id")
        return args

    def _heal_environment(self, package_name: str) -> dict[str, Any]:
        """Attempt to automatically install a missing package using uv.

        Only packages in the ``AUTO_HEAL_ALLOWLIST`` set are eligible for
        automatic installation.  All other packages must be installed
        manually by the user.

        Args:
            package_name: The name of the package that triggered the ImportError.

        Returns:
            Dict containing success boolean and the subprocess output.
        """
        try:
            # We enforce a strict mapping to hyphenated strings just in case
            safe_pkg = package_name.replace("_", "-").split(".")[0]

            # Check allowlist before attempting installation
            if safe_pkg not in AUTO_HEAL_ALLOWLIST:
                self.logger.warning(
                    f"Package '{safe_pkg}' not in auto-heal allowlist. "
                    f"Install manually with: uv add {safe_pkg}"
                )
                return {
                    "success": False,
                    "output": f"Package {safe_pkg} not in auto-heal allowlist. Install manually with: uv add {safe_pkg}",
                }

            # Subprocess to uv add the package into the current active environment/workspace
            result = subprocess.run(
                ["uv", "add", safe_pkg],
                capture_output=True,
                text=True,
                timeout=30,
                # cwd self.working_dir or root
            )

            if result.returncode == 0:
                self.logger.info(f"Successfully auto-healed dependency: {safe_pkg}")
                return {
                    "success": True,
                    "output": f"Successfully installed {safe_pkg} via uv add.",
                }
            self.logger.error(f"Auto-heal failed for {safe_pkg}: {result.stderr}")
            return {
                "success": False,
                "output": f"Failed to install {safe_pkg}. Stderr: {result.stderr}",
            }

        except Exception as e:
            self.logger.error(f"Auto-heal exception for {package_name}: {e}")
            return {"success": False, "output": f"Exception during uv add: {e!s}"}

    def _run_coverage_loop(
        self, target_path: str, max_turns: int = 5
    ) -> dict[str, Any]:
        """Autonomous testing loop (Red/Green/Refactor).

        Repeatedly executes pytest against the target_path. If failures occur,
        forwards the stack traces to a nested Hermes session for automated repair
        until the tests pass or max_turns is exhausted.
        """
        import subprocess

        turn = 0
        trace = ""
        while turn < max_turns:
            try:
                run = subprocess.run(
                    ["uv", "run", "pytest", target_path, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except subprocess.TimeoutExpired as exc:
                self.logger.error("pytest timed out after %s seconds", 120)
                return {
                    "status": "error",
                    "message": f"pytest execution timed out: {exc}",
                    "trace": "",
                }

            if run.returncode == 0:
                self.logger.info(
                    f"Coverage loop complete: {target_path} is fully green."
                )
                return {"status": "success", "turns": turn, "output": run.stdout}

            turn += 1
            self.logger.warning(
                f"Coverage loop test failure ({turn}/{max_turns}). Initiating heal."
            )

            # Extract relevant traceback lines to fit within reasonable context lengths
            trace = (run.stdout + "\n" + run.stderr).strip()
            # Feed it right back into a nested chat_session to fix the code
            repair_prompt = (
                f"You are the autonomous Coverage Loop agent.\n"
                f"I just ran pytest on {target_path} and it failed with the following traceback:\n\n"
                f"```text\n{trace}\n```\n\n"
                f"Please analyze the failure, utilize any file-editing MCP tools you have to fix "
                f"EITHER the test file OR the source file to resolve this failure correctly. "
                f"Do not use mock objects; ensure the code functionally passes."
            )

            # Spawn a distinct auto-session to resolve it
            session_id = f"coverage_loop_{Path(target_path).stem}_{turn}"
            response = self.chat_session(prompt=repair_prompt, session_name=session_id)

            if not response.is_success():
                self.logger.error(
                    "Coverage loop repair agent failed to respond cleanly."
                )
                return {
                    "status": "error",
                    "message": "Repair agent failed.",
                    "trace": trace,
                }

        return {
            "status": "failed",
            "message": f"Did not achieve green tests after {max_turns} turns.",
            "trace": trace,
        }

    # ------------------------------------------------------------------
    # Version & Diagnostics (v0.2.0+)
    # ------------------------------------------------------------------

    def get_version(self) -> str | None:
        """Get the installed Hermes CLI version string.

        Runs ``hermes version`` and parses the output.

        Returns:
            Version string (e.g. ``"0.2.0"``) or ``None`` if unavailable.
        """
        if not self._cli_available:
            return None
        try:
            import re as _re

            result = subprocess.run(
                [self.command, "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Parse version from output like "Hermes Agent v0.2.0" or "0.2.0"
            output = (result.stdout + result.stderr).strip()
            match = _re.search(r"(\d+\.\d+\.\d+)", output)
            return match.group(1) if match else output or None
        except Exception as e:
            self.logger.debug("Could not get Hermes version: %s", e)
            return None

    def run_doctor(self) -> dict[str, Any]:
        """Run ``hermes doctor`` for comprehensive health diagnostics.

        Available in Hermes CLI v0.2.0+.  Returns structured results.

        Returns:
            Dict with ``success`` boolean and ``output`` or ``error``.
        """
        if not self._cli_available:
            return {"success": False, "error": "Hermes CLI not available"}
        try:
            result = subprocess.run(
                [self.command, "doctor"],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "NO_COLOR": "1"},
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "hermes doctor timed out after 30s"}
        except Exception as e:
            self.logger.warning("hermes doctor failed: %s", e)
            return {"success": False, "error": str(e)}

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
            "fallback_model": self._fallback_model,
            "fallback_provider": self._fallback_provider,
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

    # ------------------------------------------------------------------
    # Git Worktree Isolation (v0.2.0+)
    # ------------------------------------------------------------------

    def create_worktree(self, session_id: str) -> Path | None:
        """Create an isolated git worktree for a session.

        Args:
            session_id: Session identifier used to name the worktree branch.

        Returns:
            Path to the worktree directory, or None if creation fails.
        """
        worktree_path = self._worktree_base / f"hermes-{session_id}"
        branch_name = f"hermes/{session_id}"

        try:
            self._worktree_base.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            self.logger.info(
                "Created worktree at %s (branch: %s)", worktree_path, branch_name
            )
            return worktree_path
        except subprocess.CalledProcessError as e:
            self.logger.warning("Failed to create worktree: %s", e.stderr)
            return None
        except Exception as e:
            self.logger.warning("Worktree creation error: %s", e)
            return None

    def cleanup_worktree(self, session_id: str) -> bool:
        """Remove an isolated git worktree after session completes.

        Args:
            session_id: Session identifier matching the worktree to clean up.

        Returns:
            True if cleanup succeeded.
        """
        worktree_path = self._worktree_base / f"hermes-{session_id}"
        branch_name = f"hermes/{session_id}"

        try:
            subprocess.run(
                ["git", "worktree", "remove", str(worktree_path), "--force"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.logger.info("Cleaned up worktree: %s", worktree_path)
            return True
        except Exception as e:
            self.logger.warning("Worktree cleanup failed: %s", e)
            return False

    # ------------------------------------------------------------------
    # Session Management Helpers (v1.5.x+)
    # ------------------------------------------------------------------

    def get_session_stats(self) -> dict[str, Any]:
        """Return summary statistics for the session database.

        Returns:
            dict with keys: ``session_count``, ``db_size_bytes``,
            ``oldest_session_at``, ``newest_session_at``.
        """
        with SQLiteSessionStore(self._session_db_path) as store:
            return store.get_stats()

    def fork_session(
        self, session_id: str, new_name: str | None = None
    ) -> HermesSession | None:
        """Fork an existing session into an independent child session.

        Args:
            session_id: Source session to fork from.
            new_name: Human-friendly name for the child session.

        Returns:
            The new :class:`~codomyrmex.agents.hermes.session.HermesSession`
            with all parent messages copied, or ``None`` if the source is missing.
        """
        with SQLiteSessionStore(self._session_db_path) as store:
            parent = store.load(session_id)
            if parent is None:
                self.logger.warning("Cannot fork unknown session: %s", session_id)
                return None
            child = parent.fork(new_name=new_name)
            store.save(child)
            self.logger.info(
                "Forked session %s → %s (name=%s)",
                session_id,
                child.session_id,
                child.name,
            )
            return child

    def export_session_markdown(self, session_id: str) -> str | None:
        """Export a session as formatted Markdown.

        Args:
            session_id: Session identifier.

        Returns:
            Markdown string, or ``None`` if session not found.
        """
        with SQLiteSessionStore(self._session_db_path) as store:
            return store.export_markdown(session_id)

    def batch_execute(
        self,
        prompts: list[str],
        parallel: bool = False,
        backend: str | None = None,
        timeout: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a list of prompts, returning a list of result dicts.

        Args:
            prompts: List of prompt strings.
            parallel: If ``True``, use a :class:`~concurrent.futures.ThreadPoolExecutor`
                to submit all prompts concurrently.  Defaults to ``False`` (sequential).
            backend: Override the active backend (``\"cli\"`` | ``\"ollama\"``).
                If ``None``, uses the currently configured backend.
            timeout: Per-request timeout in seconds.  If ``None``, uses the client default.

        Returns:
            List of dicts with keys ``prompt``, ``status``, ``content``, ``error``.
        """
        from codomyrmex.agents.core import AgentRequest

        if backend:
            orig_backend = self._active_backend
            self._active_backend = backend
        if timeout:
            orig_timeout = self.timeout
            self.timeout = timeout

        def _execute_one(prompt: str) -> dict[str, Any]:
            try:
                resp = self.execute(AgentRequest(prompt=prompt))
                return {
                    "prompt": prompt,
                    "status": "success" if resp.is_success() else "error",
                    "content": resp.content,
                    "error": resp.error,
                }
            except Exception as exc:
                return {
                    "prompt": prompt,
                    "status": "error",
                    "content": "",
                    "error": str(exc),
                }

        try:
            if parallel:
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor(max_workers=min(len(prompts), 8)) as ex:
                    results = list(ex.map(_execute_one, prompts))
            else:
                results = [_execute_one(p) for p in prompts]
        finally:
            if backend:
                self._active_backend = orig_backend  # type: ignore[possibly-undefined]
            if timeout:
                self.timeout = orig_timeout  # type: ignore[possibly-undefined]

        return results

    def set_system_prompt(self, session_id: str, prompt: str) -> bool:
        """Prepend (or replace) a persistent system message in a session.

        Args:
            session_id: Session identifier.  If the session does not exist it
                will be created.
            prompt: System instruction text.

        Returns:
            ``True`` on success.
        """
        with SQLiteSessionStore(self._session_db_path) as store:
            # Create session if it doesn't exist
            if not store.load(session_id):
                store.save(HermesSession(session_id=session_id))
            return store.update_system_prompt(session_id, prompt)

    def get_session_detail(self, session_id: str) -> dict[str, Any] | None:
        """Return a rich detail dictionary for a session.

        Args:
            session_id: Session identifier.

        Returns:
            dict with all session fields plus ``message_count``, ``last_message``,
            ``has_system_prompt``, or ``None`` if not found.
        """
        with SQLiteSessionStore(self._session_db_path) as store:
            return store.get_detail(session_id)

