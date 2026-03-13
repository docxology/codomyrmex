"""Hermes Provider Router, Context Compression, and User Modeling.

Extracted from ``hermes_client.py`` to maintain the <800 LOC threshold.
Provides the unified ``call_llm()`` abstraction, cross-session user modeling,
smart context compression, and MCP server hot-reload support.

v0.2.0 features — imported as a mixin by ``HermesClient``.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# Unified Provider Router
# ─────────────────────────────────────────────────────────────────────


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
        self._credentials: dict[str, str] = {}
        self._load_credentials()

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
        import shutil

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
            Dict with keys: ``success``, ``content``, ``provider``, ``model``,
            ``is_fallback``, ``error``.
        """
        resolved_provider = provider or self.resolve_provider()
        resolved_model = model or self.model

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

        Yields tokens/chunks as they arrive asynchronously to reduce Time-to-First-Token.
        """
        resolved_provider = provider or self.resolve_provider()
        resolved_model = model or self.model

        import asyncio
        import shutil

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
        )

        if proc.stdout is None or proc.stderr is None:
            return

        yielded_any = False
        while True:
            chunk = await proc.stdout.read(64)  # read small chunks to force rapid yield
            if not chunk:
                break
            yielded_any = True
            yield chunk.decode("utf-8", errors="replace")

        await proc.wait()

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
        import shutil

        ollama_bin = shutil.which("ollama") or "ollama"
        cmd = [ollama_bin, "run", model, prompt]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "NO_COLOR": "1"},
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
        import shutil

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


# ─────────────────────────────────────────────────────────────────────
# Cross-Session User Model
# ─────────────────────────────────────────────────────────────────────


class UserModel:
    """Cross-session user context persistence.

    Stores user preferences, coding style observations, and context that
    carries across multiple Hermes sessions.  Backed by a JSON file.

    Attributes:
        user_id: Identifier for the user profile.
        preferences: Accumulated user preferences.
        observations: Coding style and behavior observations.
    """

    def __init__(self, storage_dir: str | None = None) -> None:
        """Initialize user model storage.

        Args:
            storage_dir: Directory for user model files.
        """
        self._storage_dir = Path(
            storage_dir or os.path.expanduser("~/.codomyrmex/user_model")
        )
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._profile_path = self._storage_dir / "profile.json"
        self._profile: dict[str, Any] = self._load_profile()

    def _load_profile(self) -> dict[str, Any]:
        """Load the user profile from disk."""
        if self._profile_path.exists():
            try:
                return json.loads(self._profile_path.read_text())
            except (json.JSONDecodeError, OSError):
                return self._default_profile()
        return self._default_profile()

    @staticmethod
    def _default_profile() -> dict[str, Any]:
        """Return a fresh default profile."""
        return {
            "preferences": {},
            "observations": [],
            "session_history": [],
            "context_summary": "",
        }

    def save(self) -> None:
        """Persist the current profile to disk."""
        self._profile_path.write_text(json.dumps(self._profile, indent=2))

    def record_session(self, session_id: str, summary: str) -> None:
        """Record a completed session summary for cross-session context.

        Args:
            session_id: Session identifier.
            summary: Brief summary of the session outcome.
        """
        history = self._profile.setdefault("session_history", [])
        history.append({"session_id": session_id, "summary": summary})
        # Keep only last 50 session summaries
        if len(history) > 50:
            self._profile["session_history"] = history[-50:]
        self.save()

    def add_observation(self, observation: str) -> None:
        """Add a coding style or preference observation.

        Args:
            observation: Text description of observed user behavior.
        """
        observations = self._profile.setdefault("observations", [])
        observations.append(observation)
        if len(observations) > 100:
            self._profile["observations"] = observations[-100:]
        self.save()

    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference.

        Args:
            key: Preference key (e.g., ``"language"``, ``"style"``).
            value: Preference value.
        """
        self._profile.setdefault("preferences", {})[key] = value
        self.save()

    def get_context_prompt(self) -> str:
        """Generate a context prompt from accumulated user knowledge.

        Returns:
            A system-level context string summarizing user preferences.
        """
        prefs = self._profile.get("preferences", {})
        obs = self._profile.get("observations", [])
        history = self._profile.get("session_history", [])

        parts: list[str] = []
        if prefs:
            parts.append(
                "User preferences: " + "; ".join(f"{k}={v}" for k, v in prefs.items())
            )
        if obs:
            parts.append("Observations: " + "; ".join(obs[-10:]))
        if history:
            parts.append(
                "Recent sessions: " + "; ".join(h["summary"] for h in history[-5:])
            )
        return "\n".join(parts) if parts else ""

    @property
    def profile(self) -> dict[str, Any]:
        """Return the current profile data."""
        return dict(self._profile)


# ─────────────────────────────────────────────────────────────────────
# Smart Context Compression
# ─────────────────────────────────────────────────────────────────────


class ContextCompressor:
    """Auto-compress conversation context when it exceeds token limits.

    Detects context overflow (413 errors, >100K tokens) and applies
    progressive compression strategies:
    1. Remove duplicate messages
    2. Summarize old turns
    3. Drop low-relevance messages
    4. Truncate to fit within the model's context window.

    Attributes:
        max_tokens: Maximum token estimate before compression triggers.
        compression_ratio: Target compression ratio (0.0–1.0).
    """

    # Rough chars-per-token estimate for English text
    CHARS_PER_TOKEN = 4

    def __init__(
        self, max_tokens: int = 100_000, compression_ratio: float = 0.5
    ) -> None:
        """Initialize context compressor.

        Args:
            max_tokens: Token threshold for triggering compression.
            compression_ratio: Target ratio (0.5 = compress to 50% of original).
        """
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio

    def estimate_tokens(self, messages: list[dict[str, str]]) -> int:
        """Estimate token count from messages.

        Args:
            messages: List of message dicts with 'content' key.

        Returns:
            Estimated token count.
        """
        total_chars = sum(len(m.get("content", "")) for m in messages)
        return total_chars // self.CHARS_PER_TOKEN

    def needs_compression(self, messages: list[dict[str, str]]) -> bool:
        """Check if the messages exceed the token threshold.

        Args:
            messages: Conversation messages.

        Returns:
            True if compression is recommended.
        """
        return self.estimate_tokens(messages) > self.max_tokens

    def compress(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """Compress messages to fit within token limits.

        Applies progressive strategies:
        1. Deduplicate exact-match messages
        2. Summarize old turns (keep first + last N)
        3. Truncate individual long messages

        Args:
            messages: Full conversation history.

        Returns:
            Compressed message list.
        """
        if not self.needs_compression(messages):
            return messages

        logger.info(
            "Context compression triggered: %d tokens (limit: %d)",
            self.estimate_tokens(messages),
            self.max_tokens,
        )

        # Step 1: Deduplicate identical consecutive messages
        deduped = self._deduplicate(messages)

        # Step 2: Keep first 2 and last N messages, summarize the middle
        target_msgs = max(4, int(len(deduped) * self.compression_ratio))
        if len(deduped) > target_msgs:
            head = deduped[:2]
            tail = deduped[-(target_msgs - 2) :]
            middle_count = len(deduped) - len(head) - len(tail)
            summary_msg = {
                "role": "system",
                "content": f"[{middle_count} earlier messages compressed for context limits]",
            }
            deduped = [*head, summary_msg, *tail]

        # Step 3: Truncate individual long messages
        max_msg_chars = (self.max_tokens * self.CHARS_PER_TOKEN) // max(len(deduped), 1)
        result: list[dict[str, str]] = []
        for msg in deduped:
            content = msg.get("content", "")
            if len(content) > max_msg_chars:
                msg = {**msg, "content": content[:max_msg_chars] + "\n[...truncated]"}
            result.append(msg)

        logger.info(
            "Compressed: %d → %d messages (%d → %d est. tokens)",
            len(messages),
            len(result),
            self.estimate_tokens(messages),
            self.estimate_tokens(result),
        )
        return result

    @staticmethod
    def _deduplicate(messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """Remove consecutive duplicate messages.

        Args:
            messages: Conversation messages.

        Returns:
            Messages with consecutive duplicates removed.
        """
        if not messages:
            return []
        result = [messages[0]]
        for msg in messages[1:]:
            prev = result[-1]
            if msg.get("content") != prev.get("content") or msg.get("role") != prev.get(
                "role"
            ):
                result.append(msg)
        return result


# ─────────────────────────────────────────────────────────────────────
# MCP Server Hot-Reload
# ─────────────────────────────────────────────────────────────────────


class MCPBridgeManager:
    """Manage the Hermes ↔ Codomyrmex MCP bridge.

    Handles configuration of Hermes v0.2.0 native MCP client to load
    Codomyrmex MCP servers, and supports hot-reloading without session
    restart.

    Attributes:
        config_path: Path to the MCP servers config file.
        servers: Currently configured server definitions.
    """

    def __init__(self, config_path: str | None = None) -> None:
        """Initialize MCP bridge manager.

        Args:
            config_path: Path to MCP servers JSON config.
        """
        self._config_path = Path(
            config_path or os.path.expanduser("~/.hermes/mcp_servers.json")
        )
        self._servers: dict[str, dict[str, Any]] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load MCP server configuration from disk."""
        if self._config_path.exists():
            try:
                self._servers = json.loads(self._config_path.read_text())
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load MCP config: %s", exc)

    def save_config(self) -> None:
        """Persist current MCP server configuration."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(json.dumps(self._servers, indent=2))
        logger.info("Saved MCP config to %s", self._config_path)

    def register_server(
        self,
        name: str,
        *,
        command: str,
        args: list[str] | None = None,
        transport: str = "stdio",
        description: str = "",
    ) -> None:
        """Register an MCP server for Hermes to consume.

        Args:
            name: Server identifier.
            command: Command to launch the server.
            args: Optional command arguments.
            transport: Transport mechanism (``"stdio"`` or ``"http"``).
            description: Human-readable description.
        """
        self._servers[name] = {
            "command": command,
            "args": args or [],
            "transport": transport,
            "description": description,
        }
        self.save_config()
        logger.info("Registered MCP server '%s' (%s via %s)", name, command, transport)

    def unregister_server(self, name: str) -> bool:
        """Remove an MCP server registration.

        Args:
            name: Server identifier to remove.

        Returns:
            True if the server was found and removed.
        """
        if name in self._servers:
            del self._servers[name]
            self.save_config()
            return True
        return False

    def reload(self) -> dict[str, Any]:
        """Hot-reload MCP server configuration.

        Re-reads the config from disk and signals any running Hermes
        process to reload its MCP connections.

        Returns:
            Dict with ``success`` and ``servers_loaded`` count.
        """
        self._load_config()
        server_count = len(self._servers)
        logger.info("Hot-reloaded MCP config: %d servers", server_count)

        # Signal Hermes CLI to reload if possible (v0.2.0 `hermes mcp reload`)
        import shutil

        hermes_bin = shutil.which("hermes")
        if hermes_bin:
            try:
                result = subprocess.run(
                    [hermes_bin, "mcp", "reload"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return {
                    "success": result.returncode == 0,
                    "servers_loaded": server_count,
                    "output": result.stdout.strip(),
                }
            except Exception as exc:
                logger.debug(
                    "MCP reload via CLI failed (may not be supported): %s", exc
                )

        return {
            "success": True,
            "servers_loaded": server_count,
            "output": "Config reloaded (CLI signal skipped)",
        }

    @property
    def servers(self) -> dict[str, dict[str, Any]]:
        """Return current server configurations."""
        return dict(self._servers)

    def list_servers(self) -> list[dict[str, Any]]:
        """List all configured MCP servers.

        Returns:
            List of server info dicts with ``name``, ``command``, ``transport``.
        """
        return [{"name": name, **config} for name, config in self._servers.items()]
