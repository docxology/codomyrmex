"""
Test Fixtures

Fixture management and test data factory.
"""

import random
import string
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .strategies import FloatGenerator, IntGenerator, StringGenerator


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
        """Initialize this instance."""
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
        """decorator ."""
        func._fixture_name = name
        func._fixture_scope = scope
        return func
    return decorator


class TestDataFactory:
    """Factory for generating test data."""

    @staticmethod
    def email(domain: str = "test.com") -> str:
        """email ."""
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        return f"{username}@{domain}"

    @staticmethod
    def phone(country_code: str = "+1") -> str:
        """phone ."""
        number = ''.join(random.choices(string.digits, k=10))
        return f"{country_code}{number}"

    @staticmethod
    def uuid() -> str:
        """uuid ."""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def date(
        start: datetime = None,
        end: datetime = None,
    ) -> datetime:
        """date ."""
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
