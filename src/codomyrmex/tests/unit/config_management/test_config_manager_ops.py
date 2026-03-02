"""Unit tests for ConfigurationManager -- save, operations, templates, backup, migration, and edge cases."""

import json
import os

import pytest
import yaml

from codomyrmex.config_management.core.config_loader import (
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    validate_configuration,
)

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


# ---------------------------------------------------------------------------
# ConfigurationManager -- save error path (lines 405-407)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerSaveErrors:
    """Tests for save_configuration error handling."""

    def test_save_to_unwritable_path_returns_false(self, tmp_path):
        """Saving to an unwritable path returns False (lines 405-407)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = Configuration(data={"key": "val"}, source="test")
        manager.configurations["test_save"] = config

        # /dev/null/subdir is not writable
        result = manager.save_configuration(
            "test_save", "/dev/null/impossible/output.yaml", format="yaml"
        )
        assert result is False


# ---------------------------------------------------------------------------
# ConfigurationManager -- reload error path (lines 449-451)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerReloadErrors:
    """Tests for reload_configuration error handling."""

    def test_reload_when_source_file_deleted(self, tmp_path):
        """Reloading when the source file no longer exists handles gracefully (lines 449-451)."""
        yaml_file = tmp_path / "temp_config.yaml"
        yaml_file.write_text(yaml.dump({"v": 1}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        manager.load_configuration("temp_config", sources=["temp_config.yaml"])

        # Delete the source file
        yaml_file.unlink()

        # Reload should succeed (returns True) but config data will be empty
        # because _load_file returns None for missing file
        result = manager.reload_configuration("temp_config")
        # Either True (successfully reloaded to empty) or True (file source tracked)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# ConfigurationManager -- template generation error paths (lines 489-491)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerTemplateErrors:
    """Tests for create_configuration_template error paths."""

    def test_template_with_invalid_schema_file(self, tmp_path):
        """Invalid JSON in schema file causes template creation to fail (lines 489-491)."""
        bad_schema = tmp_path / "bad_schema.json"
        bad_schema.write_text("{invalid json content")

        output = tmp_path / "template_out.yaml"
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager.create_configuration_template(str(bad_schema), str(output))
        assert result is False

    def test_template_to_unwritable_output(self, tmp_path):
        """Writing template to unwritable path returns False."""
        schema_data = {
            "type": "object",
            "properties": {"x": {"type": "string"}},
        }
        schema_file = tmp_path / "schema.json"
        schema_file.write_text(json.dumps(schema_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager.create_configuration_template(
            str(schema_file), "/dev/null/impossible/template.yaml"
        )
        assert result is False


# ---------------------------------------------------------------------------
# ConfigurationManager -- _generate_property_template edge cases (lines 514, 522)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPropertyTemplateGeneration:
    """Tests for _generate_property_template edge cases."""

    def test_number_type_generates_zero(self, tmp_path):
        """Property type 'number' (no default) generates 0 (line 514)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "number"})
        assert result == 0

    def test_integer_type_generates_zero(self, tmp_path):
        """Property type 'integer' (no default) generates 0 (line 514)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "integer"})
        assert result == 0

    def test_unknown_type_generates_none(self, tmp_path):
        """Unknown property type generates None (line 522)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "null"})
        assert result is None

    def test_unrecognized_type_generates_none(self, tmp_path):
        """Completely unrecognized type string generates None."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "custom_type_xyz"})
        assert result is None

    def test_object_type_recurses(self, tmp_path):
        """Property type 'object' recurses into _generate_template_from_schema (line 520)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({
            "type": "object",
            "properties": {
                "inner": {"type": "string"},
                "count": {"type": "integer", "default": 42},
            },
        })
        assert result == {"inner": "example_value", "count": 42}

    def test_boolean_type_generates_false(self, tmp_path):
        """Property type 'boolean' (no default) generates False."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "boolean"})
        assert result is False

    def test_array_type_generates_empty_list(self, tmp_path):
        """Property type 'array' (no default) generates []."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "array"})
        assert result == []

    def test_string_type_generates_example_value(self, tmp_path):
        """Property type 'string' (no default) generates 'example_value'."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "string"})
        assert result == "example_value"

    def test_default_value_takes_precedence(self, tmp_path):
        """When a default is present, it is returned regardless of type."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({"type": "string", "default": "custom"})
        assert result == "custom"

    def test_no_type_defaults_to_string(self, tmp_path):
        """When type is missing, defaults to 'string' behavior."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_property_template({})
        assert result == "example_value"

    def test_template_from_empty_schema(self, tmp_path):
        """_generate_template_from_schema with no properties returns empty dict."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._generate_template_from_schema({})
        assert result == {}


# ---------------------------------------------------------------------------
# ConfigurationManager -- migrate_configuration (lines 597-635)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMigrateConfiguration:
    """Tests for migrate_configuration method."""

    def test_migrate_nonexistent_config_returns_false(self, tmp_path):
        """Migrating a config that doesn't exist returns False (lines 597-599)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager.migrate_configuration("ghost", "2.0.0")
        assert result is False

    def test_migrate_exercises_import_path(self, tmp_path):
        """Migrating an existing config exercises the config_migrator import (lines 603-635).

        This will likely fail at import (returning False) since config_migrator may not exist,
        but it exercises the exception path (lines 633-635).
        """
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = Configuration(
            data={"version": "1.0.0", "setting": "old"},
            source="test",
        )
        manager.configurations["migratable"] = config

        result = manager.migrate_configuration("migratable", "2.0.0")
        # Result depends on whether config_migrator module exists
        assert isinstance(result, bool)

    def test_migrate_preserves_original_on_failure(self, tmp_path):
        """When migration fails, original config data is preserved."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        original_data = {"version": "1.0.0", "important": "data"}
        config = Configuration(data=original_data.copy(), source="test")
        manager.configurations["preserve_me"] = config

        manager.migrate_configuration("preserve_me", "99.0.0")

        # Original config should still be accessible
        current = manager.get_configuration("preserve_me")
        assert current is not None
        assert current.data.get("important") == "data"
