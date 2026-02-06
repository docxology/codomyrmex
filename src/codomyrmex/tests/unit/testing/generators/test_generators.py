"""
Tests for Testing Generators Module
"""

from datetime import datetime

import pytest

from codomyrmex.testing.generators import (
    BooleanGenerator,
    ChoiceGenerator,
    DatasetGenerator,
    DateGenerator,
    EmailGenerator,
    FloatGenerator,
    IntegerGenerator,
    NameGenerator,
    RecordGenerator,
    StringGenerator,
    UUIDGenerator,
)


class TestStringGenerator:
    """Tests for StringGenerator."""

    def test_generate(self):
        """Should generate string."""
        gen = StringGenerator(min_length=5, max_length=10)
        result = gen.generate()

        assert isinstance(result, str)
        assert 5 <= len(result) <= 10

    def test_generate_many(self):
        """Should generate many strings."""
        gen = StringGenerator()
        results = gen.generate_many(5)

        assert len(results) == 5


class TestIntegerGenerator:
    """Tests for IntegerGenerator."""

    def test_generate(self):
        """Should generate integer in range."""
        gen = IntegerGenerator(min_value=10, max_value=20)
        result = gen.generate()

        assert isinstance(result, int)
        assert 10 <= result <= 20


class TestFloatGenerator:
    """Tests for FloatGenerator."""

    def test_generate(self):
        """Should generate float with precision."""
        gen = FloatGenerator(min_value=0, max_value=100, precision=2)
        result = gen.generate()

        assert isinstance(result, float)
        assert 0 <= result <= 100


class TestBooleanGenerator:
    """Tests for BooleanGenerator."""

    def test_generate(self):
        """Should generate boolean."""
        gen = BooleanGenerator()
        results = gen.generate_many(100)

        assert all(isinstance(r, bool) for r in results)
        assert any(r for r in results)
        assert any(not r for r in results)


class TestDateGenerator:
    """Tests for DateGenerator."""

    def test_generate(self):
        """Should generate date in range."""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 12, 31)
        gen = DateGenerator(start_date=start, end_date=end)

        result = gen.generate()

        assert start <= result <= end


class TestEmailGenerator:
    """Tests for EmailGenerator."""

    def test_generate(self):
        """Should generate valid email format."""
        gen = EmailGenerator()
        result = gen.generate()

        assert "@" in result
        assert "." in result


class TestUUIDGenerator:
    """Tests for UUIDGenerator."""

    def test_generate(self):
        """Should generate UUID-like string."""
        gen = UUIDGenerator()
        result = gen.generate()

        assert len(result) == 36  # 8-4-4-4-12
        assert result.count("-") == 4


class TestNameGenerator:
    """Tests for NameGenerator."""

    def test_generate(self):
        """Should generate full name."""
        gen = NameGenerator()
        result = gen.generate()

        assert " " in result


class TestChoiceGenerator:
    """Tests for ChoiceGenerator."""

    def test_generate(self):
        """Should choose from list."""
        choices = ["a", "b", "c"]
        gen = ChoiceGenerator(choices)

        results = gen.generate_many(10)
        assert all(r in choices for r in results)


class TestRecordGenerator:
    """Tests for RecordGenerator."""

    def test_generate(self):
        """Should generate record."""
        gen = RecordGenerator()
        gen.add_field("name", NameGenerator())
        gen.add_field("age", IntegerGenerator(18, 65))

        record = gen.generate()

        assert "name" in record
        assert "age" in record

    def test_generate_many(self):
        """Should generate many records."""
        gen = RecordGenerator()
        gen.add_field("id", UUIDGenerator())

        records = gen.generate_many(5)

        assert len(records) == 5
        assert all("id" in r for r in records)


class TestDatasetGenerator:
    """Tests for DatasetGenerator."""

    def test_generate(self):
        """Should generate dataset."""
        dataset = DatasetGenerator("users")
        dataset.add_column("id", IntegerGenerator())
        dataset.add_column("name", NameGenerator())

        data = dataset.generate(rows=10)

        assert len(data) == 10
        assert all("id" in row for row in data)

    def test_columns(self):
        """Should track columns."""
        dataset = DatasetGenerator("test")
        dataset.add_column("a", StringGenerator())
        dataset.add_column("b", IntegerGenerator())

        assert dataset.columns == ["a", "b"]

    def test_generate_csv(self):
        """Should generate CSV."""
        dataset = DatasetGenerator("test")
        dataset.add_column("name", NameGenerator())

        csv = dataset.generate_csv(rows=2)
        lines = csv.split('\n')

        assert lines[0] == "name"
        assert len(lines) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
