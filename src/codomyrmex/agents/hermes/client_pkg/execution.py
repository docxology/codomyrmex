"""Hermes client mixin: CLI and Ollama execution."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.core.exceptions import AgentError, AgentTimeoutError
from codomyrmex.agents.hermes.client_pkg.errors import AutoRetryException, HermesError
from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore
from codomyrmex.agents.hermes.skill_names import (
    SESSION_METADATA_HERMES_SKILLS_KEY,
    agent_context_for_hermes_skills,
    normalize_hermes_skill_names,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class HermesExecutionMixin:
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
            self.logger.debug(
                "Failed to parse `hermes config` output: %s", exc
            )  # Fall through to .env check

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

    def _execute_impl(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """Execute via the active backend, with fallback on provider errors."""
        try:
            return self._execute_primary(request, max_tokens=max_tokens)
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

    def _execute_primary(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """Execute via the primary active backend (CLI or Ollama)."""
        if self._active_backend == "ollama":
            return self._execute_via_ollama(request, max_tokens=max_tokens)
        if not self._is_cli_configured():
            self.logger.warning(
                "Hermes CLI has no API key configured — falling back to Ollama. "
                "Run 'hermes setup' in your terminal to configure an API key."
            )
            return self._execute_via_ollama(request, max_tokens=max_tokens)
        return self._execute_via_cli(request, max_tokens=max_tokens)

    def _should_fallback(self, exc: HermesError) -> bool:
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

    def _execute_via_cli(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """Execute via the NousResearch Hermes CLI."""
        from codomyrmex.agents.hermes import skill_registry

        prompt = request.prompt
        base = dict(request.context or {})
        merged = skill_registry.merged_hermes_skill_list_for_client(
            cwd=Path.cwd(),
            client_config=self.config,
            profile_disabled=self._skill_profile_disabled,
            session_skills=self._session_skills_for_next_execute,
            context=base,
        )
        ctx = dict(base)
        if merged:
            ctx["hermes_skills"] = merged
        else:
            ctx.pop("hermes_skills", None)
        skill_names = merged
        hermes_args = self._build_hermes_args(prompt, ctx)

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
                    **({"hermes_skills_loaded": skill_names} if skill_names else {}),
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
        max_tokens: int | None = None,
    ) -> AgentResponse:
        """Execute via ``ollama run <model>``.

        Args:
            request: Agent request to execute.
            model_override: Override the default Ollama model (used by fallback).

        """
        ollama_bin = shutil.which("ollama") or "ollama"
        model = model_override or self._ollama_model
        prompt = request.prompt
        cmd = [ollama_bin, "run", model]
        if max_tokens:
            # Note: This is an approximation/best effort for the CLI backend.
            # Real token limiting is usually handled at the provider level for OpenAI/OpenRouter types.
            # For local ollama run, we inject it into the prompt or hope the backend supports it.
            # However, for pure Ollama API use we would use options.
            # Here we wrap the prompt with a limit instruction.
            prompt = f"(Limit response to {max_tokens} tokens)\n{prompt}"

        cmd.append(prompt)

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

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream output from the active backend."""
        if self._active_backend == "ollama":
            yield from self._stream_via_ollama(request)
        else:
            from codomyrmex.agents.hermes import skill_registry

            prompt = request.prompt
            base = dict(request.context or {})
            merged = skill_registry.merged_hermes_skill_list_for_client(
                cwd=Path.cwd(),
                client_config=self.config,
                profile_disabled=self._skill_profile_disabled,
                session_skills=self._session_skills_for_next_execute,
                context=base,
            )
            ctx = dict(base)
            if merged:
                ctx["hermes_skills"] = merged
            else:
                ctx.pop("hermes_skills", None)
            hermes_args = self._build_hermes_args(prompt, ctx)
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
