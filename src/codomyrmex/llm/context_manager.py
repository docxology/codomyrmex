"""Token-aware context window manager.

Manages conversation context within LLM token budgets.  Supports
FIFO eviction with importance weighting—high-importance messages
(system prompts, tool results) are retained longer than low-importance
messages (older user turns).

Works with any LLM via a pluggable tokenizer; defaults to a simple
word-based estimator and can use ``tiktoken`` when available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ── Token estimation ──────────────────────────────────────────────

def _estimate_tokens(text: str) -> int:
    """Estimate token count using word-level approximation (~1.3 tokens/word)."""
    return max(1, int(len(text.split()) * 1.3))


def _tiktoken_count(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken (precise, requires tiktoken package)."""
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except (ImportError, KeyError):
        return _estimate_tokens(text)


# ── Message importance ────────────────────────────────────────────

class MessageImportance:
    """Importance levels for context window eviction priority."""

    CRITICAL = 1.0     # System prompts — never evicted
    HIGH = 0.8         # Tool results, function outputs
    NORMAL = 0.5       # Regular conversation turns
    LOW = 0.3          # Older context, greetings


_ROLE_IMPORTANCE: dict[str, float] = {
    "system": MessageImportance.CRITICAL,
    "tool": MessageImportance.HIGH,
    "assistant": MessageImportance.NORMAL,
    "user": MessageImportance.NORMAL,
}


@dataclass
class ContextMessage:
    """A message in the context window with importance metadata.

    Attributes:
        role: Message role (system, user, assistant, tool).
        content: Text content.
        importance: Eviction priority (higher = retained longer).
        token_count: Pre-computed token count.
        metadata: Optional metadata dict.
    """

    role: str
    content: str
    importance: float = MessageImportance.NORMAL
    token_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if self.token_count == 0:
            self.token_count = _estimate_tokens(self.content)
        if self.importance == MessageImportance.NORMAL:
            self.importance = _ROLE_IMPORTANCE.get(
                self.role, MessageImportance.NORMAL
            )


# ── Context Manager ───────────────────────────────────────────────

class ContextManager:
    """Token-aware sliding window context manager.

    Maintains a list of messages within a token budget. When the budget
    is exceeded, low-importance messages are evicted first (FIFO within
    the same importance tier).

    Usage::

        ctx = ContextManager(max_tokens=4096)
        ctx.add_message("system", "You are a helpful assistant.")
        ctx.add_message("user", "What is 2+2?")
        ctx.add_message("assistant", "4")

        # When budget is tight, older low-importance messages drop first
        messages = ctx.get_context()
    """

    def __init__(
        self,
        max_tokens: int = 4096,
        model: str | None = None,
        reserve_tokens: int = 256,
    ) -> None:
        """Initialize the context manager.

        Args:
            max_tokens: Maximum token budget for the context window.
            model: Optional model name for tiktoken-based counting.
            reserve_tokens: Tokens reserved for the next response.
        """
        self._max_tokens = max_tokens
        self._reserve = reserve_tokens
        self._model = model
        self._messages: list[ContextMessage] = []
        self._total_tokens = 0

    @property
    def max_tokens(self) -> int:
        """Maximum token budget."""
        return self._max_tokens

    @property
    def current_tokens(self) -> int:
        """Current total token count."""
        return self._total_tokens

    @property
    def available_tokens(self) -> int:
        """Tokens available for new content."""
        return max(0, self._max_tokens - self._reserve - self._total_tokens)

    @property
    def message_count(self) -> int:
        """Number of messages in the context."""
        return len(self._messages)

    def _count_tokens(self, text: str) -> int:
        """Count tokens using the best available method."""
        if self._model:
            return _tiktoken_count(text, self._model)
        return _estimate_tokens(text)

    def add_message(
        self,
        role: str,
        content: str,
        importance: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ContextMessage:
        """Add a message to the context window.

        If the budget is exceeded after adding, ``trim_to_budget()``
        is called automatically.

        Args:
            role: Message role.
            content: Message content.
            importance: Override importance (defaults by role).
            metadata: Optional metadata.

        Returns:
            The added ``ContextMessage``.
        """
        token_count = self._count_tokens(content)
        msg = ContextMessage(
            role=role,
            content=content,
            importance=importance or _ROLE_IMPORTANCE.get(role, MessageImportance.NORMAL),
            token_count=token_count,
            metadata=metadata or {},
        )
        self._messages.append(msg)
        self._total_tokens += token_count

        # Auto-trim if over budget
        if self._total_tokens > self._max_tokens - self._reserve:
            self.trim_to_budget()

        return msg

    def trim_to_budget(self) -> int:
        """Evict lowest-importance messages until within budget.

        Eviction order: lowest importance first, then oldest first
        within the same importance tier. Critical messages (importance
        >= 1.0) are never evicted.

        Returns:
            Number of messages evicted.
        """
        budget = self._max_tokens - self._reserve
        evicted = 0

        while self._total_tokens > budget and len(self._messages) > 1:
            # Find the lowest-importance, oldest message
            candidates = [
                (i, m) for i, m in enumerate(self._messages)
                if m.importance < MessageImportance.CRITICAL
            ]
            if not candidates:
                break  # Only critical messages remain

            # Sort by importance (asc), then by index (asc = oldest)
            candidates.sort(key=lambda x: (x[1].importance, x[0]))
            evict_idx = candidates[0][0]
            evict_msg = self._messages.pop(evict_idx)
            self._total_tokens -= evict_msg.token_count
            evicted += 1

            logger.debug(
                "Evicted message from context",
                extra={
                    "role": evict_msg.role,
                    "importance": evict_msg.importance,
                    "tokens": evict_msg.token_count,
                },
            )

        return evicted

    def get_context(self) -> list[dict[str, str]]:
        """Get the current context as LLM-compatible message dicts.

        Returns:
            List of ``{"role": ..., "content": ...}`` dicts.
        """
        return [
            {"role": m.role, "content": m.content}
            for m in self._messages
        ]

    def get_messages(self) -> list[ContextMessage]:
        """Get the raw ContextMessage objects."""
        return list(self._messages)

    def clear(self) -> None:
        """Clear all messages from the context."""
        self._messages.clear()
        self._total_tokens = 0

    def summary(self) -> dict[str, Any]:
        """Get a summary of the context state."""
        return {
            "message_count": self.message_count,
            "total_tokens": self.current_tokens,
            "max_tokens": self.max_tokens,
            "available_tokens": self.available_tokens,
            "utilization": round(
                self.current_tokens / self.max_tokens, 3
            ) if self.max_tokens > 0 else 0.0,
        }


__all__ = [
    "ContextManager",
    "ContextMessage",
    "MessageImportance",
]
