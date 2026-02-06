"""
Testing Module

Test fixtures, generators, property-based testing, and fuzzing utilities.
"""

__version__ = "0.1.0"

import functools
import random
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar
from collections.abc import Callable, Generator

T = TypeVar('T')


# ============================================================================
# Property-Based Testing
# ============================================================================

class GeneratorStrategy(ABC):
    """Abstract base for value generators."""

    @abstractmethod
    def generate(self) -> Any:
        pass


class IntGenerator(GeneratorStrategy):
    """Generate random integers."""

    def __init__(self, min_val: int = -1000, max_val: int = 1000):
        self.min_val = min_val
        self.max_val = max_val

    def generate(self) -> int:
        return random.randint(self.min_val, self.max_val)


class FloatGenerator(GeneratorStrategy):
    """Generate random floats."""

    def __init__(self, min_val: float = -1000.0, max_val: float = 1000.0):
        self.min_val = min_val
        self.max_val = max_val

    def generate(self) -> float:
        return random.uniform(self.min_val, self.max_val)


class StringGenerator(GeneratorStrategy):
    """Generate random strings."""

    def __init__(
        self,
        min_length: int = 0,
        max_length: int = 100,
        charset: str = string.ascii_letters + string.digits,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.charset = charset

    def generate(self) -> str:
        length = random.randint(self.min_length, self.max_length)
        return ''.join(random.choice(self.charset) for _ in range(length))


class ListGenerator(GeneratorStrategy):
    """Generate random lists."""

    def __init__(
        self,
        element_generator: GeneratorStrategy,
        min_length: int = 0,
        max_length: int = 20,
    ):
        self.element_generator = element_generator
        self.min_length = min_length
        self.max_length = max_length

    def generate(self) -> list[Any]:
        length = random.randint(self.min_length, self.max_length)
        return [self.element_generator.generate() for _ in range(length)]


class DictGenerator(GeneratorStrategy):
    """Generate random dictionaries."""

    def __init__(
        self,
        key_generator: GeneratorStrategy,
        value_generator: GeneratorStrategy,
        min_size: int = 0,
        max_size: int = 10,
    ):
        self.key_generator = key_generator
        self.value_generator = value_generator
        self.min_size = min_size
        self.max_size = max_size

    def generate(self) -> dict[Any, Any]:
        size = random.randint(self.min_size, self.max_size)
        return {
            self.key_generator.generate(): self.value_generator.generate()
            for _ in range(size)
        }


class OneOfGenerator(GeneratorStrategy):
    """Generate one of specified values."""

    def __init__(self, values: list[Any]):
        self.values = values

    def generate(self) -> Any:
        return random.choice(self.values)


@dataclass
class PropertyTestResult:
    """Result of a property-based test."""
    passed: bool
    iterations: int
    failures: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0
    shrunk_example: dict[str, Any] | None = None


def property_test(
    iterations: int = 100,
    **generators: GeneratorStrategy,
):
    """Decorator for property-based tests."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            failures = []
            start = datetime.now()

            for i in range(iterations):
                test_kwargs = {
                    name: gen.generate()
                    for name, gen in generators.items()
                }
                test_kwargs.update(kwargs)

                try:
                    result = func(*args, **test_kwargs)
                    if result is False:
                        failures.append(test_kwargs.copy())
                except Exception as e:
                    failures.append({
                        **test_kwargs,
                        "__error__": str(e),
                    })

            duration = (datetime.now() - start).total_seconds()

            return PropertyTestResult(
                passed=len(failures) == 0,
                iterations=iterations,
                failures=failures[:10],  # Limit stored failures
                duration_seconds=duration,
            )

        return wrapper
    return decorator


# ============================================================================
# Fuzzing
# ============================================================================

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


# ============================================================================
# Test Fixtures
# ============================================================================

@dataclass
class Fixture:
    """A test fixture."""
    name: str
    setup_fn: Callable[[], Any]
    teardown_fn: Callable[[Any], None] | None = None
    scope: str = "function"  # function, class, module, session


class FixtureManager:
    """Manage test fixtures."""

    def __init__(self):
        self._fixtures: dict[str, Fixture] = {}
        self._active: dict[str, Any] = {}

    def register(
        self,
        name: str,
        setup_fn: Callable[[], Any],
        teardown_fn: Callable[[Any], None] | None = None,
        scope: str = "function",
    ) -> None:
        """Register a fixture."""
        self._fixtures[name] = Fixture(name, setup_fn, teardown_fn, scope)

    def get(self, name: str) -> Any:
        """Get or create fixture."""
        if name not in self._active:
            fixture = self._fixtures.get(name)
            if not fixture:
                raise ValueError(f"Unknown fixture: {name}")
            self._active[name] = fixture.setup_fn()
        return self._active[name]

    def teardown(self, name: str | None = None) -> None:
        """Teardown fixture(s)."""
        if name:
            fixtures_to_teardown = [name]
        else:
            fixtures_to_teardown = list(self._active.keys())

        for fixture_name in fixtures_to_teardown:
            if fixture_name in self._active:
                fixture = self._fixtures.get(fixture_name)
                if fixture and fixture.teardown_fn:
                    fixture.teardown_fn(self._active[fixture_name])
                del self._active[fixture_name]


def fixture(name: str, scope: str = "function"):
    """Decorator to create fixtures."""
    def decorator(func: Callable) -> Callable:
        func._fixture_name = name
        func._fixture_scope = scope
        return func
    return decorator


# ============================================================================
# Test Data Generators
# ============================================================================

class TestDataFactory:
    """Factory for generating test data."""

    @staticmethod
    def email(domain: str = "test.com") -> str:
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        return f"{username}@{domain}"

    @staticmethod
    def phone(country_code: str = "+1") -> str:
        number = ''.join(random.choices(string.digits, k=10))
        return f"{country_code}{number}"

    @staticmethod
    def uuid() -> str:
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def date(
        start: datetime = None,
        end: datetime = None,
    ) -> datetime:
        start = start or datetime(2000, 1, 1)
        end = end or datetime.now()
        delta = (end - start).total_seconds()
        random_seconds = random.uniform(0, delta)
        return start + timedelta(seconds=random_seconds)

    @staticmethod
    def json_object(depth: int = 2, breadth: int = 3) -> dict[str, Any]:
        """Generate random JSON-like object."""
        if depth == 0:
            return random.choice([
                StringGenerator().generate(),
                IntGenerator().generate(),
                FloatGenerator().generate(),
                True, False, None,
            ])

        result = {}
        for _ in range(breadth):
            key = StringGenerator(5, 10).generate()
            if random.random() < 0.3:
                result[key] = TestDataFactory.json_object(depth - 1, breadth)
            else:
                result[key] = random.choice([
                    StringGenerator().generate(),
                    IntGenerator().generate(),
                    random.random(),
                ])
        return result


__all__ = [
    # Property-based testing
    "property_test",
    "PropertyTestResult",
    "GeneratorStrategy",
    "IntGenerator",
    "FloatGenerator",
    "StringGenerator",
    "ListGenerator",
    "DictGenerator",
    "OneOfGenerator",
    # Fuzzing
    "Fuzzer",
    "FuzzResult",
    "FuzzingStrategy",
    # Fixtures
    "Fixture",
    "FixtureManager",
    "fixture",
    # Data generation
    "TestDataFactory",
]
