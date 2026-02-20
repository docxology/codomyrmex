"""
Tests for Validation Schemas Module
"""

import pytest

from codomyrmex.validation.schemas import (
    Schema,
    email_schema,
    is_valid,
    url_schema,
    validate,
)


class TestSchemaTypes:
    """Tests for basic schema types."""

    def test_string_schema(self):
        """String schema should validate strings."""
        schema = Schema.string()

        assert schema.is_valid("hello")
        assert not schema.is_valid(123)
        assert not schema.is_valid(None)

    def test_string_nullable(self):
        """Nullable string should accept None."""
        schema = Schema.string(nullable=True)

        assert schema.is_valid("hello")
        assert schema.is_valid(None)

    def test_integer_schema(self):
        """Integer schema should validate integers."""
        schema = Schema.integer()

        assert schema.is_valid(42)
        assert not schema.is_valid("42")
        assert not schema.is_valid(3.14)

    def test_number_schema(self):
        """Number schema should validate numbers."""
        schema = Schema.number()

        assert schema.is_valid(42)
        assert schema.is_valid(3.14)
        assert not schema.is_valid("42")

    def test_boolean_schema(self):
        """Boolean schema should validate booleans."""
        schema = Schema.boolean()

        assert schema.is_valid(True)
        assert schema.is_valid(False)
        assert not schema.is_valid(1)
        assert not schema.is_valid("true")

    def test_array_schema(self):
        """Array schema should validate arrays."""
        schema = Schema.array()

        assert schema.is_valid([])
        assert schema.is_valid([1, 2, 3])
        assert not schema.is_valid("array")

    def test_object_schema(self):
        """Object schema should validate objects."""
        schema = Schema.object()

        assert schema.is_valid({})
        assert schema.is_valid({"key": "value"})
        assert not schema.is_valid([])


class TestStringConstraints:
    """Tests for string constraints."""

    def test_min_length(self):
        """Should validate minimum length."""
        schema = Schema.string(min_length=3)

        assert schema.is_valid("abc")
        assert schema.is_valid("abcd")
        assert not schema.is_valid("ab")

    def test_max_length(self):
        """Should validate maximum length."""
        schema = Schema.string(max_length=5)

        assert schema.is_valid("abc")
        assert schema.is_valid("abcde")
        assert not schema.is_valid("abcdef")

    def test_pattern(self):
        """Should validate against pattern."""
        schema = Schema.string(pattern=r"^\d{3}-\d{4}$")

        assert schema.is_valid("123-4567")
        assert not schema.is_valid("1234567")
        assert not schema.is_valid("abc-defg")

    def test_enum(self):
        """Should validate against enum values."""
        schema = Schema.string(enum=["red", "green", "blue"])

        assert schema.is_valid("red")
        assert schema.is_valid("green")
        assert not schema.is_valid("yellow")


class TestNumberConstraints:
    """Tests for number constraints."""

    def test_minimum(self):
        """Should validate minimum value."""
        schema = Schema.integer(minimum=0)

        assert schema.is_valid(0)
        assert schema.is_valid(100)
        assert not schema.is_valid(-1)

    def test_maximum(self):
        """Should validate maximum value."""
        schema = Schema.integer(maximum=100)

        assert schema.is_valid(0)
        assert schema.is_valid(100)
        assert not schema.is_valid(101)

    def test_range(self):
        """Should validate range."""
        schema = Schema.number(minimum=0.0, maximum=1.0)

        assert schema.is_valid(0.0)
        assert schema.is_valid(0.5)
        assert schema.is_valid(1.0)
        assert not schema.is_valid(-0.1)
        assert not schema.is_valid(1.1)


class TestArrayConstraints:
    """Tests for array constraints."""

    def test_item_type(self):
        """Should validate item types."""
        schema = Schema.array(items=Schema.string())

        assert schema.is_valid(["a", "b", "c"])
        assert not schema.is_valid([1, 2, 3])

    def test_min_items(self):
        """Should validate minimum items."""
        schema = Schema.array(min_items=2)

        assert schema.is_valid([1, 2])
        assert schema.is_valid([1, 2, 3])
        assert not schema.is_valid([1])

    def test_max_items(self):
        """Should validate maximum items."""
        schema = Schema.array(max_items=3)

        assert schema.is_valid([1])
        assert schema.is_valid([1, 2, 3])
        assert not schema.is_valid([1, 2, 3, 4])


class TestObjectConstraints:
    """Tests for object constraints."""

    def test_properties(self):
        """Should validate property types."""
        schema = Schema.object({
            "name": Schema.string(),
            "age": Schema.integer(),
        })

        assert schema.is_valid({"name": "John", "age": 30})
        assert not schema.is_valid({"name": 123, "age": 30})

    def test_required(self):
        """Should validate required fields."""
        schema = Schema.object(
            {"name": Schema.string(), "age": Schema.integer()},
            required=["name"],
        )

        assert schema.is_valid({"name": "John"})
        assert schema.is_valid({"name": "John", "age": 30})

        result = schema.validate({})
        assert not result.valid
        assert any("name" in e.path for e in result.errors)

    def test_nested_objects(self):
        """Should validate nested objects."""
        schema = Schema.object({
            "user": Schema.object({
                "name": Schema.string(),
            }),
        })

        assert schema.is_valid({"user": {"name": "John"}})
        assert not schema.is_valid({"user": {"name": 123}})


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_error_messages(self):
        """Should provide error messages."""
        schema = Schema.string(min_length=5)
        result = schema.validate("ab")

        assert not result.valid
        assert len(result.errors) == 1
        assert "at least 5" in result.errors[0].message


class TestCommonSchemas:
    """Tests for common schema helpers."""

    def test_email_schema(self):
        """Should validate emails."""
        schema = email_schema()

        assert schema.is_valid("test@example.com")
        assert schema.is_valid("user.name@domain.co.uk")
        assert not schema.is_valid("invalid")
        assert not schema.is_valid("@example.com")

    def test_url_schema(self):
        """Should validate URLs."""
        schema = url_schema()

        assert schema.is_valid("https://example.com")
        assert schema.is_valid("http://localhost:8080/path")
        assert not schema.is_valid("not a url")
        assert not schema.is_valid("ftp://example.com")


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_validate_function(self):
        """validate() should work."""
        schema = Schema.integer(minimum=0)
        result = validate(5, schema)
        assert result.valid

    def test_is_valid_function(self):
        """is_valid() should work."""
        schema = Schema.string()
        assert is_valid("test", schema) is True
        assert is_valid(123, schema) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
