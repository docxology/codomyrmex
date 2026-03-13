"""LLM token consumption tracker with StatsD emission.

Hooks into LLM client calls to count input/output tokens and emit
StatsD counters for real-time monitoring.

Example::

    tracker = TokenTracker()
    tracker.record("gpt-4o", input_tokens=150, output_tokens=80)

    stats = tracker.get_stats()
    print(stats)  # {"total_input": 150, "total_output": 80, ...}
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """A single token usage record.

    Attributes:
        model: Model name (e.g., ``"gpt-4o"``).
        input_tokens: Number of input/prompt tokens.
        output_tokens: Number of output/completion tokens.
        timestamp: Unix timestamp.
        provider: Provider name (e.g., ``"openai"``, ``"ollama"``).
        operation: Operation type (e.g., ``"chat"``, ``"embedding"``).
    """

    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    timestamp: float = field(default_factory=time.time)
    provider: str = ""
    operation: str = "chat"


class TokenTracker:
    """Tracks LLM token consumption with StatsD emission.

    Thread-safe.  Maintains per-model rolling counters and optionally
    emits StatsD gauge/counter metrics on each recording.

    Args:
        statsd_client: Optional StatsD client for real-time emission.
        max_history: Maximum number of usage records to retain.

    Example::

        tracker = TokenTracker()
        tracker.record("gpt-4o", input_tokens=200, output_tokens=100)
        print(tracker.get_model_stats("gpt-4o"))
    """

    def __init__(
        self,
        statsd_client: Any = None,
        max_history: int = 10_000,
    ) -> None:
        self._statsd = statsd_client
        self._max_history = max_history
        self._history: list[TokenUsage] = []
        self._lock = threading.Lock()

        # Per-model aggregates
        self._model_input: dict[str, int] = defaultdict(int)
        self._model_output: dict[str, int] = defaultdict(int)
        self._model_calls: dict[str, int] = defaultdict(int)

    def record(
        self,
        model: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        provider: str = "",
        operation: str = "chat",
    ) -> TokenUsage:
        """Record a token usage event.

        Args:
            model: Model name.
            input_tokens: Number of input tokens consumed.
            output_tokens: Number of output tokens generated.
            provider: Provider name.
            operation: Operation type.

        Returns:
            The recorded :class:`TokenUsage`.
        """
        usage = TokenUsage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider=provider,
            operation=operation,
        )

        with self._lock:
            self._history.append(usage)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]

            self._model_input[model] += input_tokens
            self._model_output[model] += output_tokens
            self._model_calls[model] += 1

        # StatsD emission
        if self._statsd:
            try:
                self._statsd.incr("llm.tokens.in", input_tokens)
                self._statsd.incr("llm.tokens.out", output_tokens)
                self._statsd.incr(f"llm.calls.{model.replace('.', '_')}")
            except Exception:
                logger.debug("StatsD emission failed", exc_info=True)

        logger.debug(
            "Token usage: %s in=%d out=%d (%s/%s)",
            model,
            input_tokens,
            output_tokens,
            provider,
            operation,
        )
        return usage

    def get_stats(self) -> dict[str, Any]:
        """Return aggregate token consumption statistics.

        Returns:
            Dict with ``total_input``, ``total_output``, ``total_calls``,
            ``by_model``, and ``recent_calls``.
        """
        with self._lock:
            total_in = sum(self._model_input.values())
            total_out = sum(self._model_output.values())
            total_calls = sum(self._model_calls.values())

            by_model = {
                model: {
                    "input_tokens": self._model_input[model],
                    "output_tokens": self._model_output[model],
                    "total_tokens": self._model_input[model]
                    + self._model_output[model],
                    "calls": self._model_calls[model],
                }
                for model in sorted(self._model_calls)
            }

            return {
                "total_input": total_in,
                "total_output": total_out,
                "total_tokens": total_in + total_out,
                "total_calls": total_calls,
                "by_model": by_model,
            }

    def get_model_stats(self, model: str) -> dict[str, int]:
        """Return stats for a specific model.

        Args:
            model: Model name.

        Returns:
            Dict with ``input_tokens``, ``output_tokens``, ``calls``.
        """
        with self._lock:
            return {
                "input_tokens": self._model_input.get(model, 0),
                "output_tokens": self._model_output.get(model, 0),
                "total_tokens": self._model_input.get(model, 0)
                + self._model_output.get(model, 0),
                "calls": self._model_calls.get(model, 0),
            }

    def get_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent token usage records.

        Args:
            limit: Maximum records to return.

        Returns:
            List of usage dicts (most recent first).
        """
        with self._lock:
            recent = self._history[-limit:][::-1]
            return [
                {
                    "model": u.model,
                    "input_tokens": u.input_tokens,
                    "output_tokens": u.output_tokens,
                    "provider": u.provider,
                    "operation": u.operation,
                    "timestamp": u.timestamp,
                }
                for u in recent
            ]

    def clear(self) -> None:
        """Clear all recorded data."""
        with self._lock:
            self._history.clear()
            self._model_input.clear()
            self._model_output.clear()
            self._model_calls.clear()


# Module-level singleton
_default_tracker: TokenTracker | None = None
_tracker_lock = threading.Lock()


def get_token_tracker() -> TokenTracker:
    """Get or create the module-level singleton tracker."""
    global _default_tracker
    with _tracker_lock:
        if _default_tracker is None:
            _default_tracker = TokenTracker()
        return _default_tracker


__all__ = [
    "TokenTracker",
    "TokenUsage",
    "get_token_tracker",
]
