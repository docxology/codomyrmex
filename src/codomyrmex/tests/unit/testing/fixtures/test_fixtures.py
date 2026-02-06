"""
Tests for Testing Fixtures Module
"""

import json
import tempfile
from pathlib import Path

import pytest

from codomyrmex.testing.fixtures import (
    DataFixture,
    FixtureBuilder,
    FixtureManager,
    JSONFixtureLoader,
)


class TestFixtureManager:
    """Tests for FixtureManager."""

    def test_register(self):
        """Should register fixture."""
        fixtures = FixtureManager()
        fixtures.register("test", lambda: "value")

        assert "test" in fixtures.list_fixtures()

    def test_get(self):
        """Should get fixture value."""
        fixtures = FixtureManager()
        fixtures.register("db", lambda: {"connection": True})

        value = fixtures.get("db")

        assert value["connection"] is True

    def test_get_cached(self):
        """Should cache fixture value."""
        call_count = [0]

        def factory():
            call_count[0] += 1
            return "value"

        fixtures = FixtureManager()
        fixtures.register("test", factory)

        fixtures.get("test")
        fixtures.get("test")

        assert call_count[0] == 1

    def test_cleanup(self):
        """Should cleanup fixture."""
        cleaned = [False]

        fixtures = FixtureManager()
        fixtures.register(
            "test",
            lambda: "value",
            cleanup=lambda v: cleaned.__setitem__(0, True),
        )

        fixtures.get("test")
        fixtures.cleanup("test")

        assert cleaned[0] is True

    def test_use_context(self):
        """Should work as context manager."""
        fixtures = FixtureManager()
        fixtures.register("data", lambda: [1, 2, 3])

        with fixtures.use("data") as data:
            assert data == [1, 2, 3]


class TestDataFixture:
    """Tests for DataFixture."""

    def test_access(self):
        """Should access by index."""
        data = DataFixture([{"id": 1}, {"id": 2}])

        assert data[0]["id"] == 1
        assert len(data) == 2

    def test_filter(self):
        """Should filter records."""
        data = DataFixture([
            {"name": "Alice", "active": True},
            {"name": "Bob", "active": False},
        ])

        active = data.filter(active=True)

        assert len(active) == 1
        assert active[0]["name"] == "Alice"

    def test_find(self):
        """Should find first match."""
        data = DataFixture([
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ])

        result = data.find(id=2)

        assert result["name"] == "Bob"

    def test_iterate(self):
        """Should iterate over records."""
        data = DataFixture([{"a": 1}, {"a": 2}])

        values = [r["a"] for r in data]

        assert values == [1, 2]


class TestJSONFixtureLoader:
    """Tests for JSONFixtureLoader."""

    def test_load(self):
        """Should load from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fixture file
            data = [{"id": 1, "name": "Test"}]
            (Path(tmpdir) / "users.json").write_text(json.dumps(data))

            loader = JSONFixtureLoader(tmpdir)
            fixture = loader.load("users")

            assert len(fixture) == 1
            assert fixture[0]["name"] == "Test"

    def test_cache(self):
        """Should cache loaded fixtures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "data.json").write_text('[{"x": 1}]')

            loader = JSONFixtureLoader(tmpdir)
            f1 = loader.load("data")
            f2 = loader.load("data")

            assert f1 is f2


class TestFixtureBuilder:
    """Tests for FixtureBuilder."""

    def test_build(self):
        """Should build fixture."""
        fixture = (FixtureBuilder("user")
            .with_field("id", 1)
            .with_field("name", "Test")
            .build())

        assert fixture["id"] == 1
        assert fixture["name"] == "Test"

    def test_with_fields(self):
        """Should add multiple fields."""
        fixture = (FixtureBuilder("item")
            .with_fields(a=1, b=2, c=3)
            .build())

        assert fixture == {"a": 1, "b": 2, "c": 3}

    def test_build_many(self):
        """Should build many with IDs."""
        fixtures = (FixtureBuilder("user")
            .with_field("name", "Test")
            .build_many(3))

        assert len(fixtures) == 3
        assert fixtures[0]["id"] == 1
        assert fixtures[2]["id"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
