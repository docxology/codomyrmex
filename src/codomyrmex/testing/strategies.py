"""
Testing Generators

Value generators for property-based testing and fuzzing.
"""

import random
import string
from abc import ABC, abstractmethod
from typing import Any


class GeneratorStrategy(ABC):
    """Abstract base for value generators."""

    @abstractmethod
    def generate(self) -> Any:
        """Execute Generate operations natively."""
        pass


class IntGenerator(GeneratorStrategy):
    """Generate random integers."""

    def __init__(self, min_val: int = -1000, max_val: int = 1000):
        """Execute   Init   operations natively."""
        self.min_val = min_val
        self.max_val = max_val

    def generate(self) -> int:
        """Execute Generate operations natively."""
        return random.randint(self.min_val, self.max_val)


class FloatGenerator(GeneratorStrategy):
    """Generate random floats."""

    def __init__(self, min_val: float = -1000.0, max_val: float = 1000.0):
        """Execute   Init   operations natively."""
        self.min_val = min_val
        self.max_val = max_val

    def generate(self) -> float:
        """Execute Generate operations natively."""
        return random.uniform(self.min_val, self.max_val)


class StringGenerator(GeneratorStrategy):
    """Generate random strings."""

    def __init__(
        self,
        min_length: int = 0,
        max_length: int = 100,
        charset: str = string.ascii_letters + string.digits,
    ):
        """Execute   Init   operations natively."""
        self.min_length = min_length
        self.max_length = max_length
        self.charset = charset

    def generate(self) -> str:
        """Execute Generate operations natively."""
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
        """Execute   Init   operations natively."""
        self.element_generator = element_generator
        self.min_length = min_length
        self.max_length = max_length

    def generate(self) -> list[Any]:
        """Execute Generate operations natively."""
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
        """Execute   Init   operations natively."""
        self.key_generator = key_generator
        self.value_generator = value_generator
        self.min_size = min_size
        self.max_size = max_size

    def generate(self) -> dict[Any, Any]:
        """Execute Generate operations natively."""
        size = random.randint(self.min_size, self.max_size)
        return {
            self.key_generator.generate(): self.value_generator.generate()
            for _ in range(size)
        }


class OneOfGenerator(GeneratorStrategy):
    """Generate one of specified values."""

    def __init__(self, values: list[Any]):
        """Execute   Init   operations natively."""
        self.values = values

    def generate(self) -> Any:
        """Execute Generate operations natively."""
        return random.choice(self.values)
