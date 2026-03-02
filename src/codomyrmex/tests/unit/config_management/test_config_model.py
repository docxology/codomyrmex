"""Unit tests for the Configuration data model -- get/set, dot notation, validation."""

from datetime import UTC, datetime

import pytest

from codomyrmex.config_management.core.config_loader import (
    ConfigSchema,
    Configuration,
)

# ---------------------------------------------------------------------------
# Configuration dataclass tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfiguration:
    """Tests for the Configuration dataclass."""

    def test_creation_with_defaults(self):
        """Configuration sets loaded_at automatically on creation."""
        config = Configuration(data={"key": "value"})
        assert config.data == {"key": "value"}
        assert config.source == "unknown"
        assert config.environment == "default"
        assert config.version == "1.0.0"
        assert config.metadata == {}
        assert isinstance(config.loaded_at, datetime)

    def test_get_value_simple_key(self):
        """get_value retrieves a top-level key."""
        config = Configuration(data={"host": "localhost", "port": 5432})
        assert config.get_value("host") == "localhost"
        assert config.get_value("port") == 5432

    def test_get_value_dot_notation(self):
        """get_value supports dot-separated nested key access."""
        config = Configuration(
            data={"database": {"host": "localhost", "credentials": {"user": "admin"}}}
        )
        assert config.get_value("database.host") == "localhost"
        assert config.get_value("database.credentials.user") == "admin"

    def test_get_value_missing_key_returns_default(self):
        """get_value returns the provided default for missing keys."""
        config = Configuration(data={"a": 1})
        assert config.get_value("missing") is None
        assert config.get_value("missing", "fallback") == "fallback"
        assert config.get_value("a.b.c", 42) == 42

    def test_get_value_non_dict_intermediate(self):
        """get_value returns default when an intermediate key is not a dict."""
        config = Configuration(data={"a": "string_value"})
        assert config.get_value("a.b") is None

    def test_set_value_simple_key(self):
        """set_value writes a top-level key."""
        config = Configuration(data={})
        config.set_value("host", "127.0.0.1")
        assert config.data["host"] == "127.0.0.1"

    def test_set_value_nested_creates_intermediate(self):
        """set_value creates intermediate dicts for nested keys."""
        config = Configuration(data={})
        config.set_value("db.connection.host", "localhost")
        assert config.data == {"db": {"connection": {"host": "localhost"}}}

    def test_set_value_overwrites_existing(self):
        """set_value overwrites an existing value."""
        config = Configuration(data={"port": 3000})
        config.set_value("port", 8080)
        assert config.data["port"] == 8080

    def test_to_dict_structure(self):
        """to_dict includes all expected fields."""
        config = Configuration(
            data={"key": "val"},
            source="test_source",
            environment="staging",
            version="2.0.0",
            metadata={"author": "test"},
        )
        d = config.to_dict()
        assert d["data"] == {"key": "val"}
        assert d["source"] == "test_source"
        assert d["environment"] == "staging"
        assert d["version"] == "2.0.0"
        assert d["metadata"] == {"author": "test"}
        # loaded_at should be an ISO format string
        datetime.fromisoformat(d["loaded_at"])

    def test_validate_without_schema_returns_empty(self):
        """validate() with no schema returns an empty error list."""
        config = Configuration(data={"anything": True})
        assert config.validate() == []

    def test_validate_with_schema_valid(self):
        """validate() with a valid schema returns no errors."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )
        config = Configuration(data={"name": "test"}, schema=schema)
        assert config.validate() == []

    def test_validate_with_schema_invalid(self):
        """validate() with an invalid config returns errors."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )
        config = Configuration(data={}, schema=schema)
        errors = config.validate()
        assert len(errors) >= 1

    def test_loaded_at_is_utc(self):
        """loaded_at timestamp is in UTC."""
        config = Configuration(data={})
        assert config.loaded_at.tzinfo is not None


# ---------------------------------------------------------------------------
# Configuration -- additional edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationAdditionalEdgeCases:
    """Additional edge case tests for the Configuration dataclass."""

    def test_loaded_at_always_set(self):
        """loaded_at is always populated after __post_init__."""
        config = Configuration(data={})
        assert config.loaded_at is not None
        assert isinstance(config.loaded_at, datetime)
        # Should be very recent (within last 10 seconds)
        delta = datetime.now(UTC) - config.loaded_at
        assert delta.total_seconds() < 10

    def test_to_dict_loaded_at_is_iso_string(self):
        """to_dict converts loaded_at to ISO format string."""
        config = Configuration(data={"a": 1})
        d = config.to_dict()
        # Should be parseable as ISO datetime
        parsed = datetime.fromisoformat(d["loaded_at"])
        assert parsed is not None

    def test_set_value_deeply_nested(self):
        """set_value creates multiple levels of intermediate dicts."""
        config = Configuration(data={})
        config.set_value("a.b.c.d.e", "deep")
        assert config.data["a"]["b"]["c"]["d"]["e"] == "deep"

    def test_get_value_returns_entire_subtree(self):
        """get_value with a key that points to a dict returns the full subtree."""
        config = Configuration(data={"db": {"host": "localhost", "port": 5432}})
        subtree = config.get_value("db")
        assert subtree == {"host": "localhost", "port": 5432}

    def test_metadata_field_defaults_to_empty_dict(self):
        """metadata defaults to empty dict and does not share state between instances."""
        c1 = Configuration(data={})
        c2 = Configuration(data={})
        c1.metadata["key"] = "value"
        assert c2.metadata == {}

    def test_configuration_with_all_fields(self):
        """Configuration with all fields explicitly set."""
        schema = ConfigSchema(schema={"type": "object"})
        config = Configuration(
            data={"key": "val"},
            source="explicit_source",
            schema=schema,
            environment="production",
            version="3.0.0",
            metadata={"author": "test"},
        )
        assert config.source == "explicit_source"
        assert config.environment == "production"
        assert config.version == "3.0.0"
        assert config.schema is schema
        assert config.metadata == {"author": "test"}
