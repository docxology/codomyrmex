"""FallbackChain: try agents sequentially until one succeeds.

This module provides a fallback mechanism for agent execution where multiple
agents are tried in sequence until one succeeds. This is useful for:
- Primary/secondary agent configurations
- Degrading gracefully when premium agents fail
- Trying multiple models with different capabilities

Usage::

    chain = FallbackChain[MyAgent]()
    chain.add("primary", primary_agent).add("secondary", secondary_agent)
    result = chain.execute(lambda agent: agent.complete(prompt))

Error Handling: Only catches a subset of exceptions. Configure which exceptions
trigger fallback via the handled_exceptions parameter.

Thread Safety: This implementation is NOT thread-safe.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class FallbackResult(Generic[T]):
    """Result of a fallback chain execution.

    Attributes:
        success: Whether any agent succeeded.
        agent_name: Name of the agent that succeeded (None if all failed).
        result: The successful result (None if all failed).
        error: The exception from the last failed agent (None if succeeded).
        attempts: list of (agent_name, error) tuples for each attempt.
    """

    success: bool = False
    agent_name: str | None = None
    result: Any = None
    error: Exception | None = None
    attempts: list[tuple[str, Exception]] = field(default_factory=list)


class FallbackChain(Generic[T]):
    """Chain of agents tried in order until one succeeds.

    Attributes:
        handled_exceptions: tuple of exception types that trigger fallback.

    Example::

        chain = FallbackChain[Agent]()
        chain.add("gpt-4", gpt4_agent).add("gpt-3.5", gpt35_agent)
        result = chain.execute(lambda a: a.complete(task))
        if result.success:
            print(f"Succeeded with {result.agent_name}")
        else:
            print(f"All failed: {result.error}")
    """

    def __init__(
        self,
        handled_exceptions: tuple[type, ...] = (
            ValueError,
            RuntimeError,
            AttributeError,
            OSError,
            TypeError,
        ),
    ):
        """Initialize the fallback chain.

        Args:
            handled_exceptions: Exceptions that trigger fallback to next agent.
        """
        self._agents: list[tuple[str, T]] = []
        self.handled_exceptions = handled_exceptions

    def add(self, name: str, agent: T) -> "FallbackChain[T]":
        """Append an agent to the chain. Returns self for chaining.

        Args:
            name: Identifier for this agent (for logging/tracing).
            agent: The agent instance to try.

        Returns:
            Self for method chaining.
        """
        self._agents.append((name, agent))
        return self

    def insert(self, index: int, name: str, agent: T) -> "FallbackChain[T]":
        """Insert an agent at a specific position in the chain.

        Args:
            index: Position to insert (0 = highest priority).
            name: Identifier for this agent.
            agent: The agent instance to try.

        Returns:
            Self for method chaining.
        """
        self._agents.insert(index, (name, agent))
        return self

    def remove(self, name: str) -> bool:
        """Remove an agent from the chain by name.

        Args:
            name: Name of the agent to remove.

        Returns:
            True if agent was found and removed, False otherwise.
        """
        for i, (agent_name, _) in enumerate(self._agents):
            if agent_name == name:
                self._agents.pop(i)
                return True
        return False

    @property
    def size(self) -> int:
        """Number of agents in the chain."""
        return len(self._agents)

    @property
    def is_empty(self) -> bool:
        """Check if chain has no agents."""
        return len(self._agents) == 0

    def execute(
        self,
        func: Callable[[T], Any],
        on_fallback: Callable[[str, Exception], None] | None = None,
    ) -> Any:
        """Try each agent in order; call on_fallback when falling back.

        Args:
            func: Function to apply to each agent.
            on_fallback: Optional callback called when falling back to next agent.

        Returns:
            Result from the first successful agent.

        Raises:
            Last exception if all agents fail.
            RuntimeError if chain is empty.
        """
        if not self._agents:
            raise RuntimeError("No agents in fallback chain")

        last_error: Exception | None = None

        for name, agent in self._agents:
            try:
                return func(agent)
            except self.handled_exceptions as e:
                last_error = e
                if on_fallback:
                    on_fallback(name, e)

        if last_error:
            raise last_error
        raise RuntimeError("Fallback chain exhausted")

    def execute_detailed(
        self,
        func: Callable[[T], Any],
        on_fallback: Callable[[str, Exception], None] | None = None,
    ) -> FallbackResult[T]:
        """Execute with detailed result information.

        Unlike execute(), this method always returns a FallbackResult
        rather than raising an exception.

        Args:
            func: Function to apply to each agent.
            on_fallback: Optional callback called when falling back.

        Returns:
            FallbackResult with success status and details.
        """
        if not self._agents:
            return FallbackResult(
                error=RuntimeError("No agents in fallback chain"),
            )

        attempts: list[tuple[str, Exception]] = []
        last_error: Exception | None = None

        for name, agent in self._agents:
            try:
                result = func(agent)
                return FallbackResult(
                    success=True,
                    agent_name=name,
                    result=result,
                    attempts=attempts,
                )
            except self.handled_exceptions as e:
                last_error = e
                attempts.append((name, e))
                if on_fallback:
                    on_fallback(name, e)

        return FallbackResult(
            success=False,
            error=last_error,
            attempts=attempts,
        )

    def __repr__(self) -> str:
        agent_names = [name for name, _ in self._agents]
        return f"FallbackChain(agents={agent_names}, size={self.size})"
