"""Codomyrmex wrapper around the soul.py Agent.

soul.py stores agent identity in SOUL.md and conversation history in MEMORY.md.
No database or server is required — persistent state is plain markdown.

Providers: anthropic, openai, openai-compatible (e.g. Ollama)

Optional dependency: uv sync --extra soul
"""

from __future__ import annotations

import os
from typing import Any

try:
    from soul import Agent as _SoulAgent

    HAS_SOUL: bool = True
except ImportError:
    HAS_SOUL = False
    _SoulAgent = None

from .exceptions import SoulError, SoulImportError, SoulMemoryError, SoulProviderError


class SoulAgent:
    """Persistent markdown-memory LLM agent wrapping soul.py.

    Each instance reads SOUL.md (identity/system prompt) and MEMORY.md
    (conversation log) on construction.  Calls to ``ask()`` optionally
    append the exchange back to MEMORY.md.

    Args:
        soul_path: Path to the SOUL.md identity file.
        memory_path: Path to the MEMORY.md conversation log.
        provider: LLM provider — 'anthropic', 'openai', or 'openai-compatible'.
        api_key: Provider API key.  If None, read from the appropriate
            environment variable (ANTHROPIC_API_KEY / OPENAI_API_KEY).
        model: Model name override.  Uses the provider default when None.
        base_url: Base URL for openai-compatible endpoints (e.g. Ollama at
            http://localhost:11434/v1).

    Raises:
        SoulImportError: When soul-agent is not installed.
        SoulError: When the underlying soul.py Agent cannot be constructed.
    """

    def __init__(
        self,
        soul_path: str = "SOUL.md",
        memory_path: str = "MEMORY.md",
        provider: str = "anthropic",
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        if not HAS_SOUL:
            raise SoulImportError(
                "soul-agent is not installed. Run: uv sync --extra soul"
            )

        # Resolve API key from environment when not supplied explicitly.
        if api_key is None:
            env_map = {
                "anthropic": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
            }
            env_key = env_map.get(provider, f"{provider.upper()}_API_KEY")
            api_key = os.getenv(env_key)

        try:
            self._agent = _SoulAgent(
                soul_path=soul_path,
                memory_path=memory_path,
                provider=provider,
                api_key=api_key,
                model=model,
                base_url=base_url,
            )
        except Exception as exc:
            raise SoulError(f"Failed to initialise soul agent: {exc}") from exc

        self.soul_path = soul_path
        self.memory_path = memory_path
        self.provider = provider

    def ask(self, question: str, remember: bool = True) -> str:
        """Query the agent and optionally persist the exchange to MEMORY.md.

        Args:
            question: The question or statement to send.
            remember: When True (default), append the exchange to MEMORY.md.

        Returns:
            The agent's text response.

        Raises:
            SoulProviderError: When the underlying LLM call fails.
        """
        try:
            return self._agent.ask(question, remember=remember)
        except Exception as exc:
            raise SoulProviderError(f"Agent query failed: {exc}") from exc

    def remember(self, note: str) -> None:
        """Manually append a note to MEMORY.md.

        Args:
            note: Free-form text to append.

        Raises:
            SoulMemoryError: When the write fails.
        """
        try:
            self._agent.remember(note)
        except Exception as exc:
            raise SoulMemoryError(f"Memory write failed: {exc}") from exc

    def reset_conversation(self) -> None:
        """Clear in-session conversation history without modifying MEMORY.md.

        Use this to start a fresh session while keeping long-term memory intact.
        """
        self._agent.reset_conversation()

    def memory_stats(self) -> dict[str, Any]:
        """Return file-size statistics for SOUL.md and MEMORY.md.

        Returns:
            Dictionary with keys: soul_path, memory_path, provider,
            soul_exists, soul_size_bytes, memory_exists, memory_size_bytes.
        """
        stats: dict[str, Any] = {
            "soul_path": self.soul_path,
            "memory_path": self.memory_path,
            "provider": self.provider,
        }
        for key, path in [("soul", self.soul_path), ("memory", self.memory_path)]:
            if os.path.exists(path):
                stats[f"{key}_exists"] = True
                stats[f"{key}_size_bytes"] = os.path.getsize(path)
            else:
                stats[f"{key}_exists"] = False
                stats[f"{key}_size_bytes"] = 0
        return stats
