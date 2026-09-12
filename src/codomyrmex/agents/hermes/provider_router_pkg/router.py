"""Unified provider routing."""

from __future__ import annotations

import json
import logging
import os
import shutil
import signal
import subprocess
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

class ProviderRouter:
    """Provider-agnostic LLM routing abstraction.

    Unifies CLI, Ollama, and direct API calls behind a single ``call_llm()``
    entry point.  The router resolves credentials for the configured provider
    (Nous Portal, OpenRouter, Ollama, z.ai) and dispatches accordingly.

    Attributes:
        providers: Ordered list of provider names to try.
        active_provider: The currently resolved provider.
        credentials: Cached credential lookups.

    """

    SUPPORTED_PROVIDERS = ("openrouter", "nous", "ollama", "zai", "openai", "anthropic")

    def __init__(
        self,
        primary_provider: str = "openrouter",
        fallback_provider: str | None = "ollama",
        model: str = "hermes3",
        fallback_model: str | None = None,
        env_path: str | None = None,
    ) -> None:
        """Initialize the provider router.

        Args:
            primary_provider: Primary inference provider name.
            fallback_provider: Fallback provider on primary failure.
            model: Primary model name.
            fallback_model: Fallback model name.
            env_path: Path to .env file for credential lookup.

        """
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.model = model
        self.fallback_model = fallback_model or model
        self._env_path = env_path or os.path.expanduser("~/.hermes/.env")
        self._rotation_path = os.path.expanduser("~/.hermes/rotation.json")
        self._credentials: dict[str, str] = {}
        self._cooldowns: dict[str, float] = {}  # model_id -> end_time
        self._load_credentials()
        self._ensure_rotation_config()

    def _load_credentials(self) -> None:
        """Load API credentials from environment and .env file."""
        # Environment variables take precedence
        key_map = {
            "openrouter": "OPENROUTER_API_KEY",
            "nous": "NOUS_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "zai": "ZAI_API_KEY",
        }
        for provider, env_var in key_map.items():
            val = os.environ.get(env_var)
            if val:
                self._credentials[provider] = val

        # Supplement from .env file
        if os.path.exists(self._env_path):
            try:
                with open(self._env_path) as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, _, value = line.partition("=")
                            key = key.strip()
                            value = value.strip().strip("\"'")
                            for provider, env_var in key_map.items():
                                if (
                                    key == env_var
                                    and value
                                    and provider not in self._credentials
                                ):
                                    self._credentials[provider] = value
            except OSError:
                pass

        # Ollama is always available if the binary exists
        if self._is_ollama_available():
            self._credentials.setdefault("ollama", "local")

    @staticmethod
    def _is_ollama_available() -> bool:
        """Check if the ollama binary is on PATH."""
        return bool(shutil.which("ollama"))

    def has_credentials(self, provider: str) -> bool:
        """Check if credentials are available for a provider."""
        return provider in self._credentials

    def resolve_provider(self) -> str:
        """Resolve the best available provider.

        Returns:
            Provider name that has valid credentials.

        Raises:
            RuntimeError: If no provider has valid credentials.

        """
        if self.has_credentials(self.primary_provider):
            return self.primary_provider
        if self.fallback_provider and self.has_credentials(self.fallback_provider):
            logger.info(
                "Primary provider '%s' has no credentials; using fallback '%s'",
                self.primary_provider,
                self.fallback_provider,
            )
            return self.fallback_provider
        # Try all known providers
        for provider in self.SUPPORTED_PROVIDERS:
            if self.has_credentials(provider):
                logger.info("Auto-resolved provider: %s", provider)
                return provider
        raise RuntimeError("No provider has valid credentials. Run 'hermes setup'.")

    def _ensure_rotation_config(self) -> None:
        """Ensure rotation.json exists, creating it from template if needed."""
        if not os.path.exists(self._rotation_path):
            try:
                template_path = (
                    Path(__file__).parent / "templates" / "rotation_template.json"
                )
                if template_path.exists():
                    os.makedirs(os.path.dirname(self._rotation_path), exist_ok=True)
                    shutil.copy(template_path, self._rotation_path)
                    logger.info(
                        "Created rotation config: %s",
                        self._rotation_path,
                    )
            except Exception as exc:
                logger.warning("Failed to create rotation config: %s", exc)

    def get_rotation_models(self) -> list[dict[str, Any]]:
        """Read rotation models from config.

        Returns:
            list of model config dicts, sorted by priority.

        """
        if not os.path.exists(self._rotation_path):
            return []
        try:
            with open(self._rotation_path) as f:
                data = json.load(f)
                models = data.get("rotation_models", [])
                return sorted(models, key=lambda x: x.get("priority", 99))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read rotation config: %s", exc)
            return []

    def call_llm(
        self,
        prompt: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Unified LLM invocation — provider-agnostic.

        Resolves the provider, calls the LLM, and returns a structured result.
        Falls back to the fallback provider on error.

        Args:
            prompt: The prompt text.
            provider: Override provider (auto-resolved if None).
            model: Override model name.
            timeout: Timeout in seconds.

        Returns:
            dict with keys: ``success``, ``content``, ``provider``, ``model``,
            ``is_fallback``, ``error``.

        """
        resolved_provider = provider or self.resolve_provider()
        resolved_model = model or self.model

        import time

        # Check if we should rotate
        if resolved_provider == "openrouter" and not model:
            rotation_models = self.get_rotation_models()
            for r_model in rotation_models:
                m_id = r_model["model"]
                if self._cooldowns.get(m_id, 0) > time.time():
                    continue

                logger.info("Attempting rotated model: %s", m_id)
                try:
                    res = self._dispatch(prompt, "openrouter", m_id, timeout)
                    if res["success"]:
                        return res
                except Exception as exc:
                    # If 429 specifically, add to cooldown
                    if "429" in str(exc) or "Rate limit" in str(exc):
                        cooldown = r_model.get("cooldown_seconds", 60)
                        self._cooldowns[m_id] = time.time() + cooldown
                        logger.warning(
                            "Model %s rate limited. Cooldown: %ds",
                            m_id,
                            cooldown,
                        )
                    continue

        try:
            return self._dispatch(prompt, resolved_provider, resolved_model, timeout)
        except Exception as primary_exc:
            if self.fallback_provider and resolved_provider != self.fallback_provider:
                logger.warning(
                    "Provider '%s' failed (%s); trying fallback '%s'",
                    resolved_provider,
                    primary_exc,
                    self.fallback_provider,
                )
                try:
                    result = self._dispatch(
                        prompt,
                        self.fallback_provider,
                        self.fallback_model,
                        timeout,
                    )
                    result["is_fallback"] = True
                    return result
                except Exception as fallback_exc:
                    return {
                        "success": False,
                        "content": "",
                        "provider": self.fallback_provider,
                        "model": self.fallback_model,
                        "is_fallback": True,
                        "error": f"Primary: {primary_exc}; Fallback: {fallback_exc}",
                    }
            return {
                "success": False,
                "content": "",
                "provider": resolved_provider,
                "model": resolved_model,
                "is_fallback": False,
                "error": str(primary_exc),
            }

    async def call_llm_stream(
        self,
        prompt: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        timeout: int = 120,
    ) -> AsyncIterator[str]:
        """Unified LLM streaming invocation.

        Yields tokens/chunks as they arrive to reduce Time-to-First-Token.
        """
        resolved_provider = provider or self.resolve_provider()
        resolved_model = model or self.model

        import asyncio

        env = {**os.environ, "NO_COLOR": "1"}
        if resolved_provider == "ollama":
            bin_path = shutil.which("ollama") or "ollama"
            cmd = [bin_path, "run", resolved_model, prompt]
        else:
            bin_path = shutil.which("hermes") or "hermes"
            cmd = [
                bin_path,
                "chat",
                "-q",
                prompt,
                "-Q",
                "--provider",
                resolved_provider,
            ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            start_new_session=True,
        )

        if proc.stdout is None or proc.stderr is None:
            return

        yielded_any = False
        try:
            while True:
                chunk = await asyncio.wait_for(
                    proc.stdout.read(64),
                    timeout=timeout,
                )
                if not chunk:
                    break
                yielded_any = True
                yield chunk.decode("utf-8", errors="replace")

            await asyncio.wait_for(proc.wait(), timeout=timeout)
            with suppress(TimeoutError):
                await asyncio.wait_for(proc.stderr.read(), timeout=1)
        except TimeoutError as exc:
            if hasattr(os, "killpg"):
                with suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGKILL)
            with suppress(ProcessLookupError):
                proc.kill()
            with suppress(TimeoutError):
                await asyncio.wait_for(proc.communicate(), timeout=5)
            raise RuntimeError(f"Streaming timed out after {timeout} seconds") from exc

        if proc.returncode != 0 and not yielded_any:
            err = await proc.stderr.read()
            raise RuntimeError(
                f"Streaming failed (exit {proc.returncode}): {err.decode().strip()}"
            )

    def _dispatch(
        self,
        prompt: str,
        provider: str,
        model: str,
        timeout: int,
    ) -> dict[str, Any]:
        """Dispatch a prompt to the specified provider.

        Args:
            prompt: Prompt text.
            provider: Provider name.
            model: Model name.
            timeout: Subprocess timeout.

        Returns:
            Structured result dict.

        """
        if provider == "ollama":
            return self._call_ollama(prompt, model, timeout)
        # All CLI-based providers route through `hermes chat`
        return self._call_hermes_cli(prompt, provider, model, timeout)

    @staticmethod
    def _call_ollama(prompt: str, model: str, timeout: int) -> dict[str, Any]:
        """Call Ollama directly."""
        ollama_bin = shutil.which("ollama") or "ollama"
        cmd = [ollama_bin, "run", model, prompt]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "NO_COLOR": "1"},
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Ollama {model} timed out after {timeout}s")

        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            # Check if model needs to be pulled
            if "pull" in stderr or "not found" in stderr.lower():
                logger.info("Model '%s' not found. Attempting 'ollama pull'...", model)
                try:
                    subprocess.run(
                        [ollama_bin, "pull", model],
                        capture_output=True,
                        text=True,
                        timeout=300,  # Longer timeout for pull
                        check=True,
                    )
                    # Retry once
                    proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        env={**os.environ, "NO_COLOR": "1"},
                    )
                except Exception as pull_exc:
                    raise RuntimeError(
                        f"Ollama pull failed for model '{model}': {pull_exc}"
                    )

        if proc.returncode != 0 or not proc.stdout.strip():
            raise RuntimeError(
                f"Ollama {model} failed (exit {proc.returncode}): "
                f"{proc.stderr.strip() or proc.stdout.strip()}"
            )
        return {
            "success": True,
            "content": proc.stdout.strip(),
            "provider": "ollama",
            "model": model,
            "is_fallback": False,
            "error": None,
        }

    @staticmethod
    def _call_hermes_cli(
        prompt: str,
        provider: str,
        model: str,
        timeout: int,
    ) -> dict[str, Any]:
        """Call via the Hermes CLI with a specific provider."""
        hermes_bin = shutil.which("hermes") or "hermes"
        cmd = [hermes_bin, "chat", "-q", prompt, "-Q", "--provider", provider]
        env = {**os.environ, "NO_COLOR": "1"}

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        stdout = proc.stdout.strip()
        if proc.returncode != 0 or not stdout:
            raise RuntimeError(
                f"Hermes CLI ({provider}/{model}) failed (exit {proc.returncode}): "
                f"{proc.stderr.strip() or stdout}"
            )
        return {
            "success": True,
            "content": stdout,
            "provider": provider,
            "model": model,
            "is_fallback": False,
            "error": None,
        }

    def get_provider_status(self) -> dict[str, Any]:
        """Return a summary of available providers and their credential status."""
        return {
            provider: {
                "has_credentials": self.has_credentials(provider),
                "is_primary": provider == self.primary_provider,
                "is_fallback": provider == self.fallback_provider,
            }
            for provider in self.SUPPORTED_PROVIDERS
        }
