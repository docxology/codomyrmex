"""
Fuzzing Utilities

Fuzz testing strategies and execution.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Any
from collections.abc import Callable

from .strategies import GeneratorStrategy


class FuzzingStrategy(Enum):
    """Fuzzing strategies."""
    RANDOM = "random"
    MUTATION = "mutation"
    BOUNDARY = "boundary"


@dataclass
class FuzzResult:
    """Result of a fuzz test."""
    input_data: Any
    output: Any = None
    crashed: bool = False
    exception: str | None = None
    execution_time_ms: float = 0.0


class Fuzzer:
    """Fuzz testing utility."""

    def __init__(
        self,
        strategy: FuzzingStrategy = FuzzingStrategy.RANDOM,
        max_iterations: int = 1000,
    ):
        """Execute   Init   operations natively."""
        self.strategy = strategy
        self.max_iterations = max_iterations
        self._results: list[FuzzResult] = []

    def fuzz(
        self,
        func: Callable,
        generator: GeneratorStrategy,
    ) -> list[FuzzResult]:
        """Run fuzz testing on a function."""
        self._results = []

        for _ in range(self.max_iterations):
            input_data = generator.generate()

            if self.strategy == FuzzingStrategy.BOUNDARY:
                input_data = self._apply_boundary_mutation(input_data)
            elif self.strategy == FuzzingStrategy.MUTATION:
                input_data = self._apply_mutation(input_data)

            result = self._execute_one(func, input_data)
            self._results.append(result)

        return self._results

    def _execute_one(self, func: Callable, input_data: Any) -> FuzzResult:
        """Execute function with one input."""
        import time
        start = time.time()

        try:
            output = func(input_data)
            return FuzzResult(
                input_data=input_data,
                output=output,
                execution_time_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return FuzzResult(
                input_data=input_data,
                crashed=True,
                exception=str(e),
                execution_time_ms=(time.time() - start) * 1000,
            )

    def _apply_boundary_mutation(self, value: Any) -> Any:
        """Apply boundary value mutations."""
        if isinstance(value, int):
            return random.choice([0, -1, 1, 2**31-1, -2**31, 2**63-1])
        elif isinstance(value, str):
            return random.choice(["", " ", "\n", "\x00", "a" * 10000])
        elif isinstance(value, list):
            return random.choice([[], [None], list(range(1000))])
        return value

    def _apply_mutation(self, value: Any) -> Any:
        """Apply random mutations."""
        if isinstance(value, str) and value:
            # Random character flip
            idx = random.randint(0, len(value) - 1)
            return value[:idx] + chr(random.randint(0, 255)) + value[idx+1:]
        elif isinstance(value, int):
            return value + random.randint(-10, 10)
        return value

    def get_crashes(self) -> list[FuzzResult]:
        """Get all crash results."""
        return [r for r in self._results if r.crashed]
