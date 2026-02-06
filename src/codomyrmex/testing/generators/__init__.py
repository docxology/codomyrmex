"""
Testing Generators Module

Test data generation utilities.
"""

__version__ = "0.1.0"

import hashlib
import random
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Union
from collections.abc import Callable

T = TypeVar('T')


class DataType(Enum):
    """Types of generated data."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    EMAIL = "email"
    UUID = "uuid"
    NAME = "name"
    ADDRESS = "address"
    PHONE = "phone"


@dataclass
class FieldSpec:
    """Specification for a generated field."""
    name: str
    data_type: DataType
    nullable: bool = False
    unique: bool = False
    min_value: int | float | None = None
    max_value: int | float | None = None
    choices: list[Any] | None = None
    pattern: str | None = None


class Generator(ABC):
    """Base class for data generators."""

    @abstractmethod
    def generate(self) -> Any:
        """Generate a single value."""
        pass

    def generate_many(self, count: int) -> list[Any]:
        """Generate multiple values."""
        return [self.generate() for _ in range(count)]


class StringGenerator(Generator):
    """Generates random strings."""

    def __init__(
        self,
        min_length: int = 5,
        max_length: int = 20,
        charset: str = string.ascii_letters + string.digits,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.charset = charset

    def generate(self) -> str:
        length = random.randint(self.min_length, self.max_length)
        return ''.join(random.choices(self.charset, k=length))


class IntegerGenerator(Generator):
    """Generates random integers."""

    def __init__(self, min_value: int = 0, max_value: int = 1000):
        self.min_value = min_value
        self.max_value = max_value

    def generate(self) -> int:
        return random.randint(self.min_value, self.max_value)


class FloatGenerator(Generator):
    """Generates random floats."""

    def __init__(
        self,
        min_value: float = 0.0,
        max_value: float = 100.0,
        precision: int = 2,
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.precision = precision

    def generate(self) -> float:
        value = random.uniform(self.min_value, self.max_value)
        return round(value, self.precision)


class BooleanGenerator(Generator):
    """Generates random booleans."""

    def __init__(self, true_probability: float = 0.5):
        self.true_probability = true_probability

    def generate(self) -> bool:
        return random.random() < self.true_probability


class DateGenerator(Generator):
    """Generates random dates."""

    def __init__(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        self.start_date = start_date or datetime(2020, 1, 1)
        self.end_date = end_date or datetime.now()

    def generate(self) -> datetime:
        delta = self.end_date - self.start_date
        random_days = random.randint(0, delta.days)
        return self.start_date + timedelta(days=random_days)


class EmailGenerator(Generator):
    """Generates random email addresses."""

    DOMAINS = ["example.com", "test.org", "mail.net", "demo.io"]

    def __init__(self):
        self._string_gen = StringGenerator(min_length=5, max_length=10, charset=string.ascii_lowercase)

    def generate(self) -> str:
        username = self._string_gen.generate()
        domain = random.choice(self.DOMAINS)
        return f"{username}@{domain}"


class UUIDGenerator(Generator):
    """Generates UUIDs."""

    def generate(self) -> str:
        # Simple UUID-like string
        parts = [
            ''.join(random.choices('0123456789abcdef', k=8)),
            ''.join(random.choices('0123456789abcdef', k=4)),
            ''.join(random.choices('0123456789abcdef', k=4)),
            ''.join(random.choices('0123456789abcdef', k=4)),
            ''.join(random.choices('0123456789abcdef', k=12)),
        ]
        return '-'.join(parts)


class NameGenerator(Generator):
    """Generates random names."""

    FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

    def generate(self) -> str:
        first = random.choice(self.FIRST_NAMES)
        last = random.choice(self.LAST_NAMES)
        return f"{first} {last}"


class ChoiceGenerator(Generator):
    """Generates random choice from list."""

    def __init__(self, choices: list[Any]):
        self.choices = choices

    def generate(self) -> Any:
        return random.choice(self.choices)


class RecordGenerator:
    """
    Generates structured records.

    Usage:
        gen = RecordGenerator()
        gen.add_field("name", NameGenerator())
        gen.add_field("email", EmailGenerator())
        gen.add_field("age", IntegerGenerator(18, 65))

        record = gen.generate()
        records = gen.generate_many(100)
    """

    def __init__(self):
        self._fields: dict[str, Generator] = {}

    def add_field(self, name: str, generator: Generator) -> "RecordGenerator":
        """Add a field generator."""
        self._fields[name] = generator
        return self

    def generate(self) -> dict[str, Any]:
        """Generate a single record."""
        return {name: gen.generate() for name, gen in self._fields.items()}

    def generate_many(self, count: int) -> list[dict[str, Any]]:
        """Generate multiple records."""
        return [self.generate() for _ in range(count)]


class DatasetGenerator:
    """
    Generates complete datasets.

    Usage:
        dataset = DatasetGenerator("users")
        dataset.add_column("id", UUIDGenerator())
        dataset.add_column("name", NameGenerator())
        dataset.add_column("active", BooleanGenerator())

        data = dataset.generate(rows=1000)
    """

    def __init__(self, name: str):
        self.name = name
        self._columns: dict[str, Generator] = {}

    def add_column(self, name: str, generator: Generator) -> "DatasetGenerator":
        """Add a column generator."""
        self._columns[name] = generator
        return self

    @property
    def columns(self) -> list[str]:
        """Get column names."""
        return list(self._columns.keys())

    def generate(self, rows: int = 100) -> list[dict[str, Any]]:
        """Generate dataset."""
        return [
            {col: gen.generate() for col, gen in self._columns.items()}
            for _ in range(rows)
        ]

    def generate_csv(self, rows: int = 100) -> str:
        """Generate as CSV string."""
        data = self.generate(rows)
        if not data:
            return ""

        lines = [','.join(self.columns)]
        for row in data:
            values = [str(row[col]) for col in self.columns]
            lines.append(','.join(values))

        return '\n'.join(lines)


__all__ = [
    # Enums
    "DataType",
    # Data classes
    "FieldSpec",
    # Base
    "Generator",
    # Generators
    "StringGenerator",
    "IntegerGenerator",
    "FloatGenerator",
    "BooleanGenerator",
    "DateGenerator",
    "EmailGenerator",
    "UUIDGenerator",
    "NameGenerator",
    "ChoiceGenerator",
    # Composite
    "RecordGenerator",
    "DatasetGenerator",
]
