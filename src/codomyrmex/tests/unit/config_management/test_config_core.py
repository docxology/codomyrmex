"""Comprehensive tests for config_management/core: ConfigSchema, Configuration, ConfigurationManager.

Tests the core config_loader.py module which provides:
- ConfigSchema: JSON Schema-based validation via jsonschema
- Configuration: Dataclass with dot-notation access, set, merge, to_dict
- ConfigurationManager: Multi-source loading (YAML, JSON, env), save, reload, template generation

All tests use real files (via tmp_path / tempfile), real env vars, and real dicts.
Zero mocks per project policy.
"""

import json
import os
import tempfile
from datetime import datetime, timezone

import pytest
import yaml

from codomyrmex.config_management.core.config_loader import (
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    load_configuration,
    validate_configuration,
)


# ---------------------------------------------------------------------------
# ConfigSchema tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigSchemaValidation:
    """Tests for ConfigSchema.validate() using real jsonschema validation."""

    def test_valid_object_passes(self):
        """Valid data against a simple object schema produces no errors."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            },
            title="PersonSchema",
        )
        errors = schema.validate({"name": "Alice", "age": 30})
        assert errors == []

    def test_type_mismatch_produces_error(self):
        """String where integer expected returns a validation error."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"count": {"type": "integer"}},
            },
        )
        errors = schema.validate({"count": "not_a_number"})
        assert len(errors) == 1
        assert "Validation error" in errors[0]

    def test_missing_required_field_produces_error(self):
        """Missing required field triggers validation error."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"host": {"type": "string"}},
                "required": ["host"],
            },
        )
        errors = schema.validate({})
        assert len(errors) == 1
        assert "host" in errors[0].lower() or "required" in errors[0].lower()

    def test_additional_properties_allowed_by_default(self):
        """Extra properties pass when additionalProperties is not restricted."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"a": {"type": "string"}},
            },
        )
        errors = schema.validate({"a": "hello", "extra": 999})
        assert errors == []

    def test_additional_properties_forbidden(self):
        """Extra properties fail when additionalProperties is false."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"a": {"type": "string"}},
                "additionalProperties": False,
            },
        )
        errors = schema.validate({"a": "hello", "extra": 999})
        assert len(errors) >= 1

    def test_nested_object_validation(self):
        """Nested objects are validated recursively."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "db": {
                        "type": "object",
                        "properties": {"port": {"type": "integer"}},
                        "required": ["port"],
                    }
                },
            },
        )
        # Valid nested
        assert schema.validate({"db": {"port": 5432}}) == []
        # Invalid nested
        errors = schema.validate({"db": {"port": "bad"}})
        assert len(errors) >= 1

    def test_array_validation(self):
        """Array items are validated correctly."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
            },
        )
        assert schema.validate({"tags": ["a", "b"]}) == []
        errors = schema.validate({"tags": [1, 2]})
        assert len(errors) >= 1

    def test_enum_constraint(self):
        """Enum constraints reject values outside the allowed set."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["DEBUG", "INFO", "ERROR"]},
                },
            },
        )
        assert schema.validate({"level": "INFO"}) == []
        errors = schema.validate({"level": "TRACE"})
        assert len(errors) >= 1

    def test_minimum_maximum_constraints(self):
        """Numeric min/max constraints are enforced."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                },
            },
        )
        assert schema.validate({"port": 8080}) == []
        assert len(schema.validate({"port": 0})) >= 1
        assert len(schema.validate({"port": 70000})) >= 1

    def test_empty_schema_accepts_anything(self):
        """An empty schema (no constraints) should accept any object."""
        schema = ConfigSchema(schema={})
        assert schema.validate({"anything": "goes"}) == []
        assert schema.validate(42) == []

    def test_schema_defaults(self):
        """ConfigSchema default field values are correctly set."""
        schema = ConfigSchema(schema={"type": "object"})
        assert schema.version == "draft7"
        assert schema.title == ""
        assert schema.description == ""

    @pytest.mark.parametrize(
        "data,expected_valid",
        [
            ({"name": "ok"}, True),
            ({}, False),
            ({"name": 123}, False),
            ({"name": ""}, True),  # empty string is still a string
        ],
    )
    def test_parametrized_required_string(self, data, expected_valid):
        """Parametrized validation of a required string field."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )
        errors = schema.validate(data)
        if expected_valid:
            assert errors == []
        else:
            assert len(errors) >= 1


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
# ConfigurationManager -- file loading tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerFileLoading:
    """Tests for ConfigurationManager loading from files."""

    def test_load_from_yaml_file(self, tmp_path):
        """Load configuration from a YAML file."""
        config_data = {"server": {"host": "0.0.0.0", "port": 9090}, "debug": True}
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text(yaml.dump(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("app", sources=["app.yaml"])

        assert config.data["server"]["host"] == "0.0.0.0"
        assert config.data["server"]["port"] == 9090
        assert config.data["debug"] is True

    def test_load_from_json_file(self, tmp_path):
        """Load configuration from a JSON file."""
        config_data = {"name": "myapp", "workers": 4}
        json_file = tmp_path / "app.json"
        json_file.write_text(json.dumps(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("app", sources=["app.json"])

        assert config.data["name"] == "myapp"
        assert config.data["workers"] == 4

    def test_load_from_yml_extension(self, tmp_path):
        """Load configuration from a .yml file."""
        config_data = {"key": "yml_value"}
        yml_file = tmp_path / "settings.yml"
        yml_file.write_text(yaml.dump(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("settings", sources=["settings.yml"])
        assert config.data["key"] == "yml_value"

    def test_load_configuration_from_file_direct(self, tmp_path):
        """load_configuration_from_file loads by absolute path."""
        config_data = {"direct": "load"}
        json_file = tmp_path / "direct.json"
        json_file.write_text(json.dumps(config_data))

        manager = ConfigurationManager()
        config = manager.load_configuration_from_file(str(json_file))

        assert config is not None
        assert config.data["direct"] == "load"
        assert config.source == str(json_file)

    def test_load_configuration_from_file_missing(self):
        """load_configuration_from_file returns None for missing files."""
        manager = ConfigurationManager()
        config = manager.load_configuration_from_file("/nonexistent/path/config.json")
        assert config is None

    def test_load_yaml_via_direct_path(self, tmp_path):
        """load_configuration_from_file handles YAML by extension."""
        config_data = {"yaml_key": [1, 2, 3]}
        yaml_file = tmp_path / "data.yaml"
        yaml_file.write_text(yaml.dump(config_data))

        manager = ConfigurationManager()
        config = manager.load_configuration_from_file(str(yaml_file))

        assert config is not None
        assert config.data["yaml_key"] == [1, 2, 3]

    def test_load_nonexistent_source_returns_empty_config(self, tmp_path):
        """Loading from non-existent default sources yields empty data dict."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("nonexistent_cfg")
        assert config.data == {}


# ---------------------------------------------------------------------------
# ConfigurationManager -- environment variable override tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerEnvVars:
    """Tests for environment variable loading and override."""

    def test_env_var_override(self, tmp_path):
        """Environment variables with CONFIG_NAME_ prefix override file values."""
        # Write a YAML file
        yaml_file = tmp_path / "myapp.yaml"
        yaml_file.write_text(yaml.dump({"host": "filehost", "port": 3000}))

        # Set env var with the correct prefix
        saved = {k: os.environ.get(k) for k in ("MYAPP_HOST", "MYAPP_PORT")}
        os.environ["MYAPP_HOST"] = "envhost"
        os.environ["MYAPP_PORT"] = "9999"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            config = manager.load_configuration("myapp", sources=["myapp.yaml"])

            # Env vars should override (note: env values are strings)
            assert config.data["host"] == "envhost"
            assert config.data["port"] == "9999"
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_env_var_only_matching_prefix(self, tmp_path):
        """Only env vars with the correct prefix are loaded."""
        saved = {k: os.environ.get(k) for k in ("TESTCFG_A", "OTHERCFG_B")}
        os.environ["TESTCFG_A"] = "1"
        os.environ["OTHERCFG_B"] = "2"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            config = manager.load_configuration("testcfg")

            assert "a" in config.data
            assert "b" not in config.data
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_env_source_protocol(self, tmp_path):
        """Sources with env:// protocol load specific environment variables."""
        saved = os.environ.get("MY_SECRET")
        os.environ["MY_SECRET"] = "s3cr3t"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            config = manager.load_configuration("secrets", sources=["env://MY_SECRET"])

            assert config.data.get("MY_SECRET") == "s3cr3t"
        finally:
            if saved is None:
                os.environ.pop("MY_SECRET", None)
            else:
                os.environ["MY_SECRET"] = saved

    def test_env_source_protocol_missing_raises(self, tmp_path):
        """env:// source for missing variable raises FileNotFoundError (single-source guard)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        os.environ.pop("DEFINITELY_NOT_SET_12345", None)
        with pytest.raises(FileNotFoundError, match="Configuration source not found"):
            manager.load_configuration("x", sources=["env://DEFINITELY_NOT_SET_12345"])


# ---------------------------------------------------------------------------
# ConfigurationManager -- merge / override / multi-source tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerMerge:
    """Tests for multi-source merging and override behavior."""

    def test_later_sources_override_earlier(self, tmp_path):
        """When multiple sources define the same key, later sources win."""
        base = tmp_path / "base.yaml"
        base.write_text(yaml.dump({"host": "base_host", "port": 1111}))

        override = tmp_path / "override.json"
        override.write_text(json.dumps({"host": "override_host"}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration(
            "app", sources=["base.yaml", "override.json"]
        )

        assert config.data["host"] == "override_host"
        assert config.data["port"] == 1111  # preserved from base

    def test_multiple_yaml_files_merged(self, tmp_path):
        """Multiple YAML files are merged left-to-right."""
        f1 = tmp_path / "a.yaml"
        f1.write_text(yaml.dump({"x": 1, "y": 2}))

        f2 = tmp_path / "b.yaml"
        f2.write_text(yaml.dump({"y": 20, "z": 30}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("merged", sources=["a.yaml", "b.yaml"])

        assert config.data["x"] == 1
        assert config.data["y"] == 20
        assert config.data["z"] == 30

    def test_source_tracking(self, tmp_path):
        """The config.source string lists all loaded sources."""
        f1 = tmp_path / "s1.yaml"
        f1.write_text(yaml.dump({"a": 1}))
        f2 = tmp_path / "s2.json"
        f2.write_text(json.dumps({"b": 2}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("tracked", sources=["s1.yaml", "s2.json"])

        assert "s1.yaml" in config.source
        assert "s2.json" in config.source


# ---------------------------------------------------------------------------
# ConfigurationManager -- save tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerSave:
    """Tests for saving configurations to files."""

    def test_save_as_yaml(self, tmp_path):
        """save_configuration writes valid YAML."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = Configuration(data={"host": "localhost", "port": 5432}, source="test")
        manager.configurations["db"] = config

        output = tmp_path / "output" / "db.yaml"
        result = manager.save_configuration("db", str(output), format="yaml")

        assert result is True
        loaded = yaml.safe_load(output.read_text())
        assert loaded["host"] == "localhost"
        assert loaded["port"] == 5432

    def test_save_as_json(self, tmp_path):
        """save_configuration writes valid JSON."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = Configuration(data={"key": "value"}, source="test")
        manager.configurations["app"] = config

        output = tmp_path / "output" / "app.json"
        result = manager.save_configuration("app", str(output), format="json")

        assert result is True
        loaded = json.loads(output.read_text())
        assert loaded["key"] == "value"

    def test_save_nonexistent_config_returns_false(self, tmp_path):
        """Saving a config that was never loaded returns False."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager.save_configuration("ghost", str(tmp_path / "out.yaml"))
        assert result is False


# ---------------------------------------------------------------------------
# ConfigurationManager -- reload / list / get tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerOperations:
    """Tests for reload, list, get operations."""

    def test_list_configurations(self, tmp_path):
        """list_configurations returns names of all loaded configs."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        manager.configurations["alpha"] = Configuration(data={"a": 1}, source="test")
        manager.configurations["beta"] = Configuration(data={"b": 2}, source="test")

        names = manager.list_configurations()
        assert set(names) == {"alpha", "beta"}

    def test_get_configuration_exists(self, tmp_path):
        """get_configuration returns the Configuration object by name."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = Configuration(data={"x": 10}, source="test")
        manager.configurations["myconfig"] = config

        result = manager.get_configuration("myconfig")
        assert result is config

    def test_get_configuration_missing(self, tmp_path):
        """get_configuration returns None for unknown names."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        assert manager.get_configuration("nope") is None

    def test_reload_configuration(self, tmp_path):
        """reload_configuration re-reads from the original source files."""
        yaml_file = tmp_path / "reloadable.yaml"
        yaml_file.write_text(yaml.dump({"version": 1}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("reloadable", sources=["reloadable.yaml"])
        assert config.data["version"] == 1

        # Modify the file
        yaml_file.write_text(yaml.dump({"version": 2}))

        success = manager.reload_configuration("reloadable")
        assert success is True
        assert manager.get_configuration("reloadable").data["version"] == 2

    def test_reload_nonexistent_config(self, tmp_path):
        """reload_configuration returns False for unknown config names."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        assert manager.reload_configuration("ghost") is False

    def test_validate_all_configurations(self, tmp_path):
        """validate_all_configurations returns errors for invalid configs."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )
        manager = ConfigurationManager(config_dir=str(tmp_path))
        # Valid config
        manager.configurations["good"] = Configuration(
            data={"name": "ok"}, source="test", schema=schema
        )
        # Invalid config
        manager.configurations["bad"] = Configuration(
            data={}, source="test", schema=schema
        )

        results = manager.validate_all_configurations()
        assert "bad" in results
        assert "good" not in results


# ---------------------------------------------------------------------------
# ConfigurationManager -- template generation tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerTemplates:
    """Tests for configuration template generation from schemas."""

    def test_generate_template_from_schema_yaml(self, tmp_path):
        """create_configuration_template writes a YAML template from a JSON schema."""
        schema_data = {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer", "default": 8080},
                "debug": {"type": "boolean"},
                "tags": {"type": "array"},
                "settings": {
                    "type": "object",
                    "properties": {
                        "timeout": {"type": "number", "default": 30},
                    },
                },
            },
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema_data))

        output_file = tmp_path / "template.yaml"
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager.create_configuration_template(
            str(schema_file), str(output_file)
        )

        assert result is True
        template = yaml.safe_load(output_file.read_text())
        assert template["host"] == "example_value"
        assert template["port"] == 8080
        assert template["debug"] is False
        assert template["tags"] == []
        assert template["settings"]["timeout"] == 30

    def test_generate_template_from_schema_json(self, tmp_path):
        """create_configuration_template writes a JSON template."""
        schema_data = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "default": "app"},
            },
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema_data))

        output_file = tmp_path / "template.json"
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager.create_configuration_template(
            str(schema_file), str(output_file)
        )

        assert result is True
        template = json.loads(output_file.read_text())
        assert template["name"] == "app"

    def test_generate_template_missing_schema(self, tmp_path):
        """create_configuration_template returns False for missing schema file."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager.create_configuration_template(
            "/nonexistent/schema.json", str(tmp_path / "out.yaml")
        )
        assert result is False


# ---------------------------------------------------------------------------
# ConfigurationManager -- file:// protocol tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerFileProtocol:
    """Tests for file:// source protocol."""

    def test_file_protocol_loads_absolute_path(self, tmp_path):
        """Sources with file:// protocol load from absolute path."""
        config_data = {"from_file_protocol": True}
        json_file = tmp_path / "abs.json"
        json_file.write_text(json.dumps(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration(
            "proto", sources=[f"file://{json_file}"]
        )
        assert config.data.get("from_file_protocol") is True


# ---------------------------------------------------------------------------
# ConfigurationManager -- schema validation integration
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerSchemaValidation:
    """Tests for loading with JSON schema validation."""

    def test_load_with_json_schema_file(self, tmp_path):
        """load_configuration validates against a JSON schema file."""
        schema_data = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema_data))

        config_data = {"name": "valid_app"}
        config_file = tmp_path / "app.json"
        config_file.write_text(json.dumps(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration(
            "app", sources=["app.json"], schema_path=str(schema_file)
        )

        assert config.schema is not None
        assert config.validate() == []

    def test_load_with_yaml_schema_file(self, tmp_path):
        """Schema files can also be in YAML format."""
        schema_data = {
            "type": "object",
            "properties": {"port": {"type": "integer"}},
        }
        schema_file = tmp_path / "schema.yaml"
        schema_file.write_text(yaml.dump(schema_data))

        config_data = {"port": 8080}
        config_file = tmp_path / "srv.yaml"
        config_file.write_text(yaml.dump(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration(
            "srv", sources=["srv.yaml"], schema_path=str(schema_file)
        )

        assert config.schema is not None
        assert config.validate() == []


# ---------------------------------------------------------------------------
# ConfigurationManager -- environment-specific loading
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerEnvironments:
    """Tests for environment-based config directory structure."""

    def test_environment_from_env_var(self, tmp_path):
        """ConfigurationManager reads ENVIRONMENT env var."""
        saved = os.environ.get("ENVIRONMENT")
        os.environ["ENVIRONMENT"] = "production"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            assert manager.environment == "production"
        finally:
            if saved is None:
                os.environ.pop("ENVIRONMENT", None)
            else:
                os.environ["ENVIRONMENT"] = saved

    def test_default_environment(self, tmp_path):
        """Default environment is 'development'."""
        saved = os.environ.pop("ENVIRONMENT", None)
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            assert manager.environment == "development"
        finally:
            if saved is not None:
                os.environ["ENVIRONMENT"] = saved

    def test_environment_specific_config(self, tmp_path):
        """Environment-specific configs in environments/<env>/ are loaded."""
        saved = os.environ.get("ENVIRONMENT")
        os.environ["ENVIRONMENT"] = "staging"
        try:
            # Create environment-specific config
            env_dir = tmp_path / "environments" / "staging"
            env_dir.mkdir(parents=True)
            env_config = env_dir / "app.yaml"
            env_config.write_text(yaml.dump({"env_key": "staging_value"}))

            manager = ConfigurationManager(config_dir=str(tmp_path))
            # Use default sources (which include environments/<env>/app.yaml)
            config = manager.load_configuration("app")
            assert config.data.get("env_key") == "staging_value"
        finally:
            if saved is None:
                os.environ.pop("ENVIRONMENT", None)
            else:
                os.environ["ENVIRONMENT"] = saved


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_validate_configuration_no_schema(self):
        """validate_configuration returns empty list when no schema."""
        config = Configuration(data={"key": "val"})
        result = validate_configuration(config)
        assert result == []

    def test_validate_configuration_with_schema(self):
        """validate_configuration delegates to config.validate()."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
            },
        )
        good = Configuration(data={"x": 1}, schema=schema)
        bad = Configuration(data={}, schema=schema)

        assert validate_configuration(good) == []
        assert len(validate_configuration(bad)) >= 1


# ---------------------------------------------------------------------------
# ConfigurationManager -- backup tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerBackup:
    """Tests for configuration backup functionality."""

    def test_backup_creates_copy(self, tmp_path):
        """create_migration_backup creates a backup with data copy."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        original_data = {"version": "1.0.0", "setting": "original"}
        config = Configuration(data=original_data, source="test")
        manager.configurations["myconf"] = config

        success = manager.create_migration_backup("myconf")
        assert success is True

        backup_names = [
            n for n in manager.list_configurations() if n.startswith("myconf_backup")
        ]
        assert len(backup_names) == 1

        backup = manager.get_configuration(backup_names[0])
        assert backup.data["setting"] == "original"

    def test_backup_is_independent_copy(self, tmp_path):
        """Modifying original config does not affect backup."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = Configuration(data={"val": "before"}, source="test")
        manager.configurations["cfg"] = config

        manager.create_migration_backup("cfg")
        config.data["val"] = "after"

        backup_names = [
            n for n in manager.list_configurations() if n.startswith("cfg_backup")
        ]
        backup = manager.get_configuration(backup_names[0])
        assert backup.data["val"] == "before"

    def test_backup_nonexistent_config(self, tmp_path):
        """Backup of non-existent config returns False."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        assert manager.create_migration_backup("nope") is False


# ---------------------------------------------------------------------------
# Edge cases and error handling
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEdgeCases:
    """Edge case and error handling tests."""

    def test_empty_yaml_file(self, tmp_path):
        """Loading an empty YAML file results in None data (yaml.safe_load returns None)."""
        empty_yaml = tmp_path / "empty.yaml"
        empty_yaml.write_text("")

        manager = ConfigurationManager(config_dir=str(tmp_path))
        # _load_file returns None for empty YAML (yaml.safe_load("") -> None)
        config = manager.load_configuration("empty", sources=["empty.yaml"])
        assert config.data == {}

    def test_malformed_json_file(self, tmp_path):
        """Malformed JSON file is handled gracefully (logged, returns None from _load_file)."""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{not valid json")

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("bad", sources=["bad.json"])
        assert config.data == {}

    def test_config_dir_auto_created(self, tmp_path):
        """ConfigurationManager creates config_dir if it does not exist."""
        new_dir = tmp_path / "new_config_dir"
        assert not new_dir.exists()

        manager = ConfigurationManager(config_dir=str(new_dir))
        assert os.path.isdir(manager.config_dir)

    def test_set_value_overwrites_non_dict_intermediate(self):
        """set_value replaces a non-dict intermediate with a dict when setting nested keys."""
        config = Configuration(data={"a": "plain_string"})
        config.set_value("a.b", "nested")
        assert config.data["a"] == {"b": "nested"}

    @pytest.mark.parametrize(
        "format_name,extension,loader",
        [
            ("yaml", ".yaml", yaml.safe_load),
            ("json", ".json", json.loads),
        ],
    )
    def test_save_roundtrip(self, tmp_path, format_name, extension, loader):
        """Save and reload a config preserves data for both formats."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        original = {"host": "localhost", "port": 5432, "debug": True}
        config = Configuration(data=original, source="test")
        manager.configurations["rt"] = config

        output = tmp_path / f"roundtrip{extension}"
        manager.save_configuration("rt", str(output), format=format_name)

        loaded = loader(output.read_text())
        assert loaded == original
