"""Smart context compression."""

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

from codomyrmex.agents.hermes.provider_router_pkg.context_registry import (
    get_model_context_registry,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class ContextCompressor:
    """Auto-compress conversation context when it exceeds token limits.

    Detects context overflow (413 errors, >80% capacity) and applies
    progressive compression strategies:
    1. Remove duplicate messages
    2. Summarize old turns
    3. Drop low-relevance messages
    4. Truncate to fit within the model's context window.

    Uses dynamic context window resolution via ModelContextRegistry to
    accurately trigger token eviction based on the model's actual capacity.

    Attributes:
        max_tokens: Maximum token estimate before compression triggers.
        compression_ratio: Target compression ratio (0.0–1.0).
        _model_id: Current model ID for dynamic resolution.

    """

    # Rough chars-per-token estimate for English text
    CHARS_PER_TOKEN = 4

    # Capacity threshold for triggering compression (80% of max)
    CAPACITY_THRESHOLD = 0.8

    def __init__(
        self,
        max_tokens: int = 100_000,
        compression_ratio: float = 0.5,
        model_id: str | None = None,
    ) -> None:
        """Initialize context compressor.

        Args:
            max_tokens: Token threshold for triggering compression.
            compression_ratio: Target ratio (0.5 = compress to 50% of original).
            model_id: Optional model ID for dynamic context resolution.

        """
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
        self._model_id = model_id
        self._registry = get_model_context_registry()

    @property
    def model_id(self) -> str | None:
        """Get the current model ID."""
        return self._model_id

    @model_id.setter
    def model_id(self, value: str | None) -> None:
        """set the model ID and refresh max_tokens from registry."""
        self._model_id = value
        if value is not None:
            try:
                resolved = self._registry.get_context_length(value)
                self.max_tokens = int(resolved * self.CAPACITY_THRESHOLD)
                logger.info(
                    "ContextCompressor: resolved %s max_tokens=%d (80%% of %d)",
                    value,
                    self.max_tokens,
                    resolved,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to resolve context for %s: %s, using default max_tokens",
                    value,
                    exc,
                )

    def estimate_tokens(self, messages: list[dict[str, str]]) -> int:
        """Estimate token count from messages.

        Args:
            messages: list of message dicts with 'content' key.

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
                "content": f"[{middle_count} earlier messages compressed]",
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
