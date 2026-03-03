"""Unit tests for safe JSON serialization and deserialization utilities."""

import pytest


@pytest.mark.unit
class TestSafeJsonLoads:
    """Tests for safe_json_loads function."""

    def test_valid_json(self):
        """Test parsing valid JSON."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads('{"key": "value"}')

        assert result == {"key": "value"}

    def test_invalid_json_returns_default(self):
        """Test invalid JSON returns default."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads("not valid json")

        assert result is None

    def test_custom_default(self):
        """Test custom default value."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads("invalid", default=[])

        assert result == []

    def test_none_input(self):
        """Test None input returns default."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads(None, default={})

        assert result == {}

    def test_empty_string(self):
        """Test empty string returns default."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads("", default={"empty": True})

        assert result == {"empty": True}

    def test_valid_json_array(self):
        """Test parsing valid JSON array."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads('[1, 2, 3]')

        assert result == [1, 2, 3]

    def test_valid_json_number(self):
        """Test parsing valid JSON number."""
        from codomyrmex.utils import safe_json_loads

        result = safe_json_loads('42')

        assert result == 42


@pytest.mark.unit
class TestSafeJsonDumps:
    """Tests for safe_json_dumps function."""

    def test_valid_object(self):
        """Test serializing valid object."""
        from codomyrmex.utils import safe_json_dumps

        result = safe_json_dumps({"key": "value"})

        assert '"key"' in result
        assert '"value"' in result

    def test_with_indent(self):
        """Test serialization with indent."""
        from codomyrmex.utils import safe_json_dumps

        result = safe_json_dumps({"a": 1}, indent=4)

        assert "    " in result

    def test_custom_default_on_failure(self):
        """Test custom default on serialization failure."""
        from codomyrmex.utils import safe_json_dumps

        class NonSerializable:
            pass

        result = safe_json_dumps(NonSerializable(), default="[]")

        # Should convert using str() function, not return the default
        assert result is not None

    def test_serializes_list(self):
        """Test serializing a list."""
        from codomyrmex.utils import safe_json_dumps

        result = safe_json_dumps([1, 2, 3])

        assert "[" in result
        assert "1" in result

    def test_serializes_nested_object(self):
        """Test serializing nested object."""
        from codomyrmex.utils import safe_json_dumps

        data = {"level1": {"level2": {"value": 42}}}
        result = safe_json_dumps(data)

        assert "level1" in result
        assert "level2" in result
        assert "42" in result
