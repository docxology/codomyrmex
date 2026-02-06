"""
Testing Fixtures Module

Test fixture management and setup.
"""

__version__ = "0.1.0"

import json
import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar
from collections.abc import Callable

T = TypeVar('T')


class FixtureScope(Enum):
    """Scope of a fixture."""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    SESSION = "session"


@dataclass
class FixtureDefinition:
    """Definition of a fixture."""
    name: str
    factory: Callable[[], Any]
    scope: FixtureScope = FixtureScope.FUNCTION
    cleanup: Callable[[Any], None] | None = None
    dependencies: list[str] = field(default_factory=list)


@dataclass
class FixtureInstance:
    """An instantiated fixture."""
    name: str
    value: Any
    scope: FixtureScope
    created_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return f"Fixture({self.name})"


class FixtureManager:
    """
    Manages test fixtures.

    Usage:
        fixtures = FixtureManager()

        # Register fixtures
        fixtures.register("db", lambda: create_test_db())
        fixtures.register("user", lambda: create_test_user(), cleanup=lambda u: u.delete())

        # Use fixtures
        with fixtures.use("db") as db:
            # test with db
            pass
    """

    def __init__(self):
        self._definitions: dict[str, FixtureDefinition] = {}
        self._instances: dict[str, FixtureInstance] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        factory: Callable[[], Any],
        scope: FixtureScope = FixtureScope.FUNCTION,
        cleanup: Callable[[Any], None] | None = None,
        dependencies: list[str] | None = None,
    ) -> "FixtureManager":
        """Register a fixture."""
        self._definitions[name] = FixtureDefinition(
            name=name,
            factory=factory,
            scope=scope,
            cleanup=cleanup,
            dependencies=dependencies or [],
        )
        return self

    def get(self, name: str) -> Any:
        """Get or create a fixture instance."""
        if name in self._instances:
            return self._instances[name].value

        definition = self._definitions.get(name)
        if not definition:
            raise KeyError(f"Fixture not found: {name}")

        # Resolve dependencies first
        for dep in definition.dependencies:
            self.get(dep)

        # Create instance
        value = definition.factory()
        instance = FixtureInstance(
            name=name,
            value=value,
            scope=definition.scope,
        )

        with self._lock:
            self._instances[name] = instance

        return value

    def cleanup(self, name: str) -> None:
        """Clean up a fixture instance."""
        if name not in self._instances:
            return

        definition = self._definitions.get(name)
        instance = self._instances[name]

        if definition and definition.cleanup:
            definition.cleanup(instance.value)

        with self._lock:
            del self._instances[name]

    def cleanup_all(self) -> None:
        """Clean up all fixtures."""
        for name in list(self._instances.keys()):
            self.cleanup(name)

    @contextmanager
    def use(self, name: str):
        """Context manager for using a fixture."""
        value = self.get(name)
        try:
            yield value
        finally:
            definition = self._definitions.get(name)
            if definition and definition.scope == FixtureScope.FUNCTION:
                self.cleanup(name)

    def list_fixtures(self) -> list[str]:
        """List all registered fixtures."""
        return list(self._definitions.keys())


class DataFixture:
    """
    Pre-defined data fixture.

    Usage:
        users = DataFixture([
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ])

        assert users[0]["name"] == "Alice"
        assert len(users) == 2
    """

    def __init__(self, data: list[dict[str, Any]]):
        self._data = data

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def filter(self, **kwargs) -> list[dict[str, Any]]:
        """Filter records by field values."""
        results = []
        for record in self._data:
            match = all(record.get(k) == v for k, v in kwargs.items())
            if match:
                results.append(record)
        return results

    def find(self, **kwargs) -> dict[str, Any] | None:
        """Find first matching record."""
        filtered = self.filter(**kwargs)
        return filtered[0] if filtered else None

    def all(self) -> list[dict[str, Any]]:
        """Get all records."""
        return list(self._data)


class JSONFixtureLoader:
    """
    Loads fixtures from JSON files.

    Usage:
        loader = JSONFixtureLoader("tests/fixtures")
        users = loader.load("users")
    """

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self._cache: dict[str, DataFixture] = {}

    def load(self, name: str) -> DataFixture:
        """Load fixture by name."""
        if name in self._cache:
            return self._cache[name]

        file_path = self.base_path / f"{name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {file_path}")

        with open(file_path) as f:
            data = json.load(f)

        fixture = DataFixture(data if isinstance(data, list) else [data])
        self._cache[name] = fixture

        return fixture

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()


class FixtureBuilder:
    """
    Fluent builder for creating fixture data.

    Usage:
        user = (FixtureBuilder("user")
            .with_field("id", 1)
            .with_field("name", "Test User")
            .with_field("active", True)
            .build())
    """

    def __init__(self, name: str):
        self.name = name
        self._data: dict[str, Any] = {}

    def with_field(self, key: str, value: Any) -> "FixtureBuilder":
        """Add a field."""
        self._data[key] = value
        return self

    def with_fields(self, **kwargs) -> "FixtureBuilder":
        """Add multiple fields."""
        self._data.update(kwargs)
        return self

    def build(self) -> dict[str, Any]:
        """Build the fixture."""
        return dict(self._data)

    def build_many(self, count: int, id_field: str = "id") -> list[dict[str, Any]]:
        """Build multiple fixtures with incremental IDs."""
        result = []
        for i in range(count):
            data = dict(self._data)
            data[id_field] = i + 1
            result.append(data)
        return result


__all__ = [
    # Enums
    "FixtureScope",
    # Data classes
    "FixtureDefinition",
    "FixtureInstance",
    # Core
    "FixtureManager",
    "DataFixture",
    "JSONFixtureLoader",
    "FixtureBuilder",
]
