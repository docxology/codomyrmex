"""FallbackChain: try agents sequentially until one succeeds."""

from collections.abc import Callable
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class FallbackChain(Generic[T]):
    """
    Chain of agents tried in order until one succeeds.

    Usage:
        chain = FallbackChain[MyAgent]()
        chain.add("primary", primary_agent).add("secondary", secondary_agent)
        result = chain.execute(lambda agent: agent.complete(prompt))
    """

    def __init__(self):
        self._agents: list[tuple[str, T]] = []

    def add(self, name: str, agent: T) -> "FallbackChain[T]":
        """Append an agent to the chain. Returns self for chaining."""
        self._agents.append((name, agent))
        return self

    def execute(
        self,
        func: Callable[[T], Any],
        on_fallback: Callable[[str, Exception], None] | None = None,
    ) -> Any:
        """Try each agent in order; call on_fallback when falling back."""
        last_error: Exception | None = None

        for name, agent in self._agents:
            try:
                return func(agent)
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                last_error = e
                if on_fallback:
                    on_fallback(name, e)

        if last_error:
            raise last_error
        raise RuntimeError("No agents in fallback chain")
