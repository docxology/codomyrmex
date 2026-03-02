"""Turn-based conversation history with summarization."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Turn:
    """A single conversation turn.

    Attributes:
        role: Speaker role (``user``, ``assistant``, ``system``).
        content: Message content.
        timestamp: When sent.
        metadata: Extra data.
    """

    role: str
    content: str
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def word_count(self) -> int:
        return len(self.content.split())


class ConversationHistory:
    """Track multi-turn conversations.

    Usage::

        history = ConversationHistory()
        history.add("user", "Hello")
        history.add("assistant", "Hi there!")
        print(history.summary())
    """

    def __init__(self, max_turns: int = 1000) -> None:
        self._turns: list[Turn] = []
        self._max_turns = max_turns

    def add(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> Turn:
        """add ."""
        turn = Turn(role=role, content=content, metadata=metadata or {})
        self._turns.append(turn)
        if len(self._turns) > self._max_turns:
            self._turns = self._turns[-self._max_turns:]
        return turn

    @property
    def turn_count(self) -> int:
        return len(self._turns)

    def last(self, n: int = 1) -> list[Turn]:
        """last ."""
        return self._turns[-n:]

    def by_role(self, role: str) -> list[Turn]:
        return [t for t in self._turns if t.role == role]

    def summary(self) -> dict[str, Any]:
        """summary ."""
        total_words = sum(t.word_count for t in self._turns)
        role_counts = {}
        for t in self._turns:
            role_counts[t.role] = role_counts.get(t.role, 0) + 1
        return {
            "turns": self.turn_count,
            "total_words": total_words,
            "by_role": role_counts,
        }

    def clear(self) -> None:
        """clear ."""
        self._turns.clear()

    def to_messages(self) -> list[dict[str, str]]:
        """Export as LLM-compatible messages list."""
        return [{"role": t.role, "content": t.content} for t in self._turns]


__all__ = ["ConversationHistory", "Turn"]
